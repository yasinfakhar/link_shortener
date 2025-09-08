import re
from urlextract import URLExtract
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, HttpUrl
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from src.db.sql_alchemy import Database
from src.auth.utils.get_token import authenticate_user
from src.link.services.link_service import LinkService
from src.util.response import global_response, GlobalResponse

router = APIRouter(prefix="/l")
database = Database()
service = LinkService()


async def get_db() -> AsyncSession:
    async for db in database.get_db():
        yield db


class LinkCreateInput(BaseModel):
    original_url: str
    preferred_code: Optional[str] = Field(None, description="Optional preferred short code")


class LinkUpdateInput(BaseModel):
    original_url: Optional[str] = None
    short_code: Optional[str] = None


class LinkOutput(BaseModel):
    id: int
    original_url: str
    short_code: str
    user_id: Optional[str] = None

    class Config:
        from_attributes = True


class TextProcessInput(BaseModel):
    text: str = Field(..., description="Text containing URLs to be shortened")
    base_url: str = Field("http://localhost:8005", description="Base URL for short links")


class ProcessedTextOutput(BaseModel):
    processed_text: str = Field(..., description="Text with URLs replaced with shortened versions")
    shortened_links: Dict[str, str] = Field(
        ...,
        description="Mapping of original URLs to their shortened versions"
    )


@router.post("", response_model=GlobalResponse[LinkOutput, dict])
async def create_link(
    input: LinkCreateInput,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(authenticate_user),
):
    try:
        link = await service.create_link(
            db, original_url=input.original_url, preferred_code=input.preferred_code
        )
        return global_response(link)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{short_code}", response_model=GlobalResponse[LinkOutput, dict])
async def get_link(short_code: str, db: AsyncSession = Depends(get_db)):
    try:
        link = await service.get_by_code(db, short_code)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link not found"
            )
        
        # Ensure the URL has a scheme
        original_url = link.original_url
        if not (original_url.startswith('http://') or original_url.startswith('https://')):
            original_url = f'http://{original_url}'
            
        return RedirectResponse(
            url=original_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )


@router.get("", response_model=GlobalResponse[List[LinkOutput], dict])
async def list_links(db: AsyncSession = Depends(get_db), user_id: Optional[str] = None):
    links = await service.list_links(db)
    return global_response(links)


def _extract_urls(text: str) -> List[str]:
    """Extract all URLs from the given text."""

    extractor = URLExtract()
    urls = extractor.find_urls(text)
    return urls


@router.post(
    "/process-text",
    response_model=GlobalResponse[ProcessedTextOutput, dict],
    status_code=status.HTTP_200_OK
)
async def process_text(
    input: TextProcessInput,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(authenticate_user)
):
    """
    Process text to find and shorten all URLs.
    
    This endpoint takes a text input, finds all URLs in it, shortens each URL,
    and returns the processed text with shortened URLs along with a mapping
    of original to shortened URLs.
    """
    try:
        urls = _extract_urls(input.text)
        if not urls:
            return global_response(ProcessedTextOutput(
                processed_text=input.text,
                shortened_links={}
            ))

        shortened_links = {}
        processed_text = input.text

        for url in set(urls):  # Use set to process each unique URL only once
            try:
                # Create short link
                link = await service.create_link(
                    db,
                    original_url=url,
                    preferred_code=None
                )
                # Build the shortened URL
                short_url = f"{input.base_url}/l/{link.short_code}"
                shortened_links[url] = short_url
                # Replace all occurrences of this URL in the text
                processed_text = processed_text.replace(url, short_url)
            except Exception as e:
                # If shortening fails for a URL, keep the original
                print(f"Failed to shorten URL {url}: {str(e)}")
                continue

        return global_response(ProcessedTextOutput(
            processed_text=processed_text,
            shortened_links=shortened_links
        ))

    except Exception as e:
        print(f"Error processing text: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the text"
        )


@router.put("/{link_id}", response_model=GlobalResponse[LinkOutput, dict])
async def update_link(
    link_id: int,
    input: LinkUpdateInput,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(authenticate_user),
):
    try:
        link = await service.update_link(db, link_id, input.original_url, input.short_code)
        return global_response(link)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{link_id}", response_model=GlobalResponse[dict, dict])
async def delete_link(
    link_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(authenticate_user),
):
    await service.delete_link(db, link_id)
    return global_response({"deleted": True})
