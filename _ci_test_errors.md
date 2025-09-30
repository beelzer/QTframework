# Test Markdown File

This file has intentional errors for CI testing.

```
Code block without language specifier
```

## Duplicate Header

Some content here.

## Duplicate Header

This triggers MD024 (duplicate heading) if it wasn't disabled.

This line is really long and exceeds 80 characters which would trigger MD013 line length but we have it disabled in our config so it should pass.
