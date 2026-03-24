# images-from-bold

Fetch image thumbnails from the [BOLD](https://boldsystems.org) (Barcode of Life Data Systems) database for specimen process IDs and render them as markdown.

## No API key required

This script uses BOLD's public CAOS (Context-Aware Object Storage) API endpoints:

| Step | URL |
|------|-----|
| Check for image | `https://caos.boldsystems.org/api/images?processids=<processid>` |
| Retrieve image | `https://caos.boldsystems.org/api/objects/<objectid>` |

The first endpoint returns a JSON array like:
```json
[{"processid": "BAYS528-24", "objectid": "abc123xyz"}]
```
An empty array means no image exists for that process ID.

The `objectid` is then appended to the image URL to form the direct link to the image file.

## Requirements

- Python 3.6+
- No external packages — uses stdlib only (`urllib`, `json`, `argparse`)

## Usage

```bash
# Single process ID
python fetch_bold_thumbnails.py BAYS528-24

# Multiple process IDs
python fetch_bold_thumbnails.py BAYS528-24 BBF341-13 ABINP144-21

# From a file (one process ID per line, lines starting with # are ignored)
python fetch_bold_thumbnails.py --file processids.txt

# Save output to a markdown file
python fetch_bold_thumbnails.py BAYS528-24 > thumbnails.md
```

## Output

For each process ID the script prints one line to stdout:

- **Image found**: markdown image syntax ready to embed anywhere markdown is rendered
  ```
  ![BAYS528-24](https://caos.boldsystems.org/api/objects/abc123xyz)
  ```
- **No image**: an HTML comment (invisible in rendered markdown)
  ```
  <!-- BAYS528-24: no image found -->
  ```

You can paste the output directly into GitHub comments, Obsidian notes, Jupyter notebooks, or any other markdown-rendering tool to display the specimen photographs.

## Notes on thumbnails

BOLD's CAOS system auto-generates multiple thumbnail sizes for specimen images. The `/api/objects/<objectid>` URL serves the image file directly. If you need a specific thumbnail size, contact [BOLD support](mailto:support@boldsystems.org) for documentation on size parameters, as these are not publicly documented.

## Relationship to bold-library-curation

This script is based on the image-detection logic in [`lyndallp/bold-library-curation_lpfork`](https://github.com/lyndallp/bold-library-curation_lpfork), specifically:
- `lib/BCDM/Criteria/HAS_IMAGE.pm` — CAOS API endpoints and batch size
- `workflow/scripts/assess_images.pl` — URL length limits and rate limiting

Those scripts assess whether images exist as part of a quality-grading pipeline. This script focuses purely on retrieving the image URL and formatting it for display.
