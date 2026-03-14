# Truck DMS - GitHub Pages Deployment

This repository contains the GitHub Pages site for Truck DMS, built with Jekyll.

## 🌐 Live Site

Visit the live site at: **https://yourusername.github.io/truck-dms**

## 🚀 Quick Start

### For Users
1. **Download** the latest release from the [Releases](https://github.com/yourusername/truck-dms/releases) page
2. **Extract** the ZIP file to your desired location
3. **Run** `start_dms_simple.bat` for automatic setup
4. **Access** the application at `http://localhost:5000`

### For Developers
1. **Fork** this repository
2. **Clone** your fork locally
3. **Install Ruby and Jekyll** (see [Jekyll Docs](https://jekyllrb.com/docs/installation/))
4. **Run locally**: `bundle install && bundle exec jekyll serve`
5. **Open** `http://localhost:4000` to preview changes

## 📁 Project Structure

```
truck-dms/
├── _config.yml              # Jekyll configuration
├── _layouts/
│   └── default.html       # Default page layout
├── _posts/
│   └── *.md              # Blog posts and announcements
├── assets/
│   ├── css/              # Custom CSS files
│   ├── js/               # Custom JavaScript files
│   └── images/           # Images and media
├── index.md                # Homepage content
├── Gemfile               # Ruby dependencies
└── README_JEKYLL.md     # This file
```

## 🛠️ Development

### Local Development

1. **Install Dependencies**:
   ```bash
   gem install bundler
   bundle install
   ```

2. **Run Local Server**:
   ```bash
   bundle exec jekyll serve
   ```

3. **Access Site**:
   Open `http://localhost:4000` in your browser

### Building for Production

```bash
bundle exec jekyll build
```

The built site will be in the `_site` directory.

## 🚀 Deployment

### Automatic Deployment
The site is automatically deployed to GitHub Pages when:
- Changes are pushed to the `main` branch
- Pull requests are merged to `main`
- The GitHub Actions workflow completes successfully

### Manual Deployment
1. **Build the site**:
   ```bash
   bundle exec jekyll build
   ```

2. **Deploy to GitHub Pages**:
   - Go to repository Settings → Pages
   - Select source: Deploy from a branch
   - Choose branch: `gh-pages`
   - Save settings

## 📝 Content Management

### Adding New Pages
1. Create a new `.md` file in the root directory
2. Add front matter:
   ```yaml
   ---
   layout: default
   title: "Page Title"
   description: "Page description"
   ---
   ```
3. Write your content in Markdown
4. Commit and push changes

### Adding Blog Posts
1. Create a new `.md` file in `_posts/` directory
2. Name with date: `YYYY-MM-DD-title.md`
3. Add front matter:
   ```yaml
   ---
   layout: default
   title: "Post Title"
   date: 2025-03-14 12:00:00 +0000
   categories: [category]
   tags: [tag1, tag2]
   ---
   ```
4. Write your post content in Markdown
5. Commit and push changes

## 🎨 Customization

### Modifying Styles
1. Edit `_layouts/default.html` to change the layout
2. Add custom CSS in the `<style>` block
3. Or create separate CSS files in `assets/css/`

### Adding Custom JavaScript
1. Create JS files in `assets/js/`
2. Include them in `_layouts/default.html`:
   ```html
   <script src="{{ '/assets/js/custom.js' | relative_url }}"></script>
   ```

### Using Custom Fonts
Add to the `<head>` section in `_layouts/default.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

## 🔧 Configuration

### Site Settings
Edit `_config.yml` to customize:
- `title`: Site title
- `description`: Site description
- `baseurl`: Repository name (e.g., "/truck-dms")
- `url`: GitHub Pages URL

### Jekyll Plugins
The site uses these Jekyll plugins:
- `jekyll-feed`: RSS feed generation
- `jekyll-sitemap`: XML sitemap
- `jekyll-seo-tag`: SEO optimization

## 📊 Analytics

### Google Analytics
Add to `_layouts/default.html`:
```html
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔍 SEO

### Meta Tags
The site includes:
- Responsive meta viewport
- Page titles and descriptions
- Open Graph tags for social sharing
- Structured data markup

### Sitemap
Automatically generated at `/sitemap.xml` for search engines.

## 📱 Mobile Optimization

- Responsive design with CSS Grid and Flexbox
- Touch-friendly navigation
- Optimized images and loading performance
- Mobile-first development approach

## 🌍 Browser Support

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge
- Opera

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Make** your changes
4. **Commit** your changes: `git commit -m "Add feature"`
5. **Push** to your fork: `git push origin feature-name`
6. **Create** a Pull Request

## 📄 License

This project is open source and available under the MIT License.

---

**Truck DMS** - Streamlining document management for trucking professionals.
