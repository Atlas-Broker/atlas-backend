# S3 Storage Layer

## Overview

S3 client for storing artifacts like chart images, PDF reports, and exports.

## Status

**Future enhancement** - Not required for MVP but architecture-ready.

## Planned Usage

```python
from app.db.s3.client import upload_bytes

# Upload chart image
url = await upload_bytes(
    data=chart_image_bytes,
    object_name=f"charts/{run_id}/nvda_analysis.png",
    content_type="image/png"
)
```

## Configuration

Set AWS credentials in `.env`:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `S3_BUCKET_NAME`
