from __future__ import annotations

from pathlib import Path

from src.core.contracts import Document
from src.core.exceptions import IngestionError, ValidationError
from src.security.file_validation import ALLOWED_EXTENSIONS


def load_document(file_path: str | Path) -> Document:
    """
    Load a source file from disk and return a Document DTO.

    Supports .pdf, .txt, .md, .html, .htm.
    Raises IngestionError on loading failure.
    Raises ValidationError on unsupported file type or missing file.
    """
    path = Path(file_path)

    if not path.exists():
        raise IngestionError(f"File not found: {path}")

    suffix = path.suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type '{suffix}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    try:
        if suffix == ".pdf":
            return _load_pdf(path)
        elif suffix in {".html", ".htm"}:
            return _load_html(path)
        else:
            return _load_text(path)
    except (IngestionError, ValidationError):
        raise
    except Exception as exc:
        raise IngestionError(f"Failed to load '{path.name}': {exc}") from exc


# ---------------------------------------------------------------------------
# Internal loaders
# ---------------------------------------------------------------------------


def _doc_id(path: Path) -> str:
    """Derive a stable, human-readable doc_id from the filename stem."""
    return path.stem.lower().replace(" ", "_")


def _base_metadata(path: Path) -> dict:
    return {
        "file_name": path.name,
        "source": str(path.resolve()),
        "file_type": path.suffix.lower(),
    }


def _load_text(path: Path) -> Document:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="latin-1")

    return Document(
        doc_id=_doc_id(path),
        text=text,
        source=str(path.resolve()),
        file_type=path.suffix.lower(),
        page_number=None,
        metadata=_base_metadata(path),
    )


def _load_pdf(path: Path) -> Document:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise IngestionError(
            "pypdf is required for PDF loading. "
            "Install it with: pip install pypdf"
        ) from exc

    reader = PdfReader(str(path))
    page_texts = [
        page.extract_text() or ""
        for page in reader.pages
    ]
    full_text = "\n\n".join(t for t in page_texts if t.strip())

    meta = _base_metadata(path)
    meta["total_pages"] = len(reader.pages)

    return Document(
        doc_id=_doc_id(path),
        text=full_text,
        source=str(path.resolve()),
        file_type=".pdf",
        page_number=None,
        metadata=meta,
    )


def _load_html(path: Path) -> Document:
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise IngestionError(
            "beautifulsoup4 is required for HTML loading. "
            "Install it with: pip install beautifulsoup4 lxml"
        ) from exc

    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="latin-1")

    soup = BeautifulSoup(raw, "lxml")
    for tag in soup(["script", "style", "head"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    return Document(
        doc_id=_doc_id(path),
        text=text,
        source=str(path.resolve()),
        file_type=path.suffix.lower(),
        page_number=None,
        metadata=_base_metadata(path),
    )
