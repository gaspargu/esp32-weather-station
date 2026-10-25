# Documentation Images

[Project overview](../../README.md)

Store documentation images here so GitHub can display them using relative Markdown paths.

## Folder layout

```text
docs/images/
  architecture.png          System data-flow diagram
  hardware/
    esp32-station.jpg        Assembled station photo
  dashboard/
    dashboard-capture.png    Desktop dashboard screenshot
```

Use descriptive filenames for additional wiring photos or mobile screenshots. Convert HEIC originals to JPG before adding them; renaming the extension does not convert the format. Keep originals outside Git when they are not needed for documentation.

## Add and reference an image

1. Save the image in the appropriate folder. Use lowercase, hyphenated filenames without spaces.
2. Use JPG for photographs and PNG for interface screenshots. Crop unnecessary areas and compress images; aim for less than 1 MB per image when practical.
3. Check that no Wi-Fi passwords, tokens, personal data, or sensitive terminal output are visible. Label screenshots that use simulated data rather than real sensor readings.
4. Add the Markdown reference only after the image exists. Relative paths are resolved from the Markdown file containing the reference, not from the repository root.

In the root `README.md`:

```markdown
![ESP32-S3 weather station with AM2302 sensor](docs/images/hardware/esp32-station.jpg)

![Weather station dashboard on desktop](docs/images/dashboard/dashboard-capture.png)
```

In `frontend/README.md`:

```markdown
![Weather station dashboard on desktop](../docs/images/dashboard/dashboard-capture.png)
```

In `docs/hardware.md`:

```markdown
![ESP32-S3 weather station with AM2302 sensor](images/hardware/esp32-station.jpg)
```

Keep the main README focused on one station photo and one dashboard overview. Put wiring close-ups in the hardware guide and additional desktop/mobile screenshots in the frontend guide. Use descriptive alternative text for accessibility.
