## Plan: Move footer CSS to external stylesheet

## TL;DR
Move the inline CSS from footer.html into static/css/styles.css, add a single <link> to that stylesheet inside the site's base <head> (found in index.html), and adjust how the background image URL is referenced (static CSS cannot use Jinja). This ensures styles load early, cache properly, and avoids flash-of-unstyled-content.

## Steps
1. In static/css/styles.css, add the CSS rules currently in footer.html inside <style>…</style>. Adjust the background-image URL to use a static path (not Jinja). For example:
```css
body {
    background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('/static/images/new_radio_background.png');
    background-size: cover;
    background-attachment: fixed;
    background-repeat: no-repeat;
    background-position: center;
    color: white;
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}
```
2. Create a base template (e.g., templates/base.html) that includes the common <head> elements and links to styles.css.

3. Update all page templates (index.html, sources.html, proposal_detail.html, listen_player.html, etc.) to extend base.html and remove any duplicate <head> content.

4. Remove the inline <style> from footer.html, leaving only the <footer> markup.

5. Test the site locally to ensure styles load correctly and the background image appears as expected.

## Rationale
* Performance: External stylesheets load once and cache, reducing page load times on subsequent visits.
* Maintainability: Centralized CSS makes it easier to update styles without modifying multiple templates.
* User Experience: Prevents flash-of-unstyled-content (FOUC) by loading styles before rendering the page.
## Testing
* Verify that the background image and styles appear correctly on all pages.
* Use browser developer tools to confirm styles.css is loaded in the <head>.
* Check for any console errors related to missing styles or images.
