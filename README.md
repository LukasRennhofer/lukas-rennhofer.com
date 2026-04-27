# lukas-rennhofer.com

This is my personal minimalist portfolio. It doesn’t rely on the typical “web-dev hell” frameworks I’d rather avoid. The goal was to build a fast, reliable system for my site so I don’t need to depend on AI tools for web development and can understand every part of it down to the last character.

## CMS

It’s not really a CMS in the traditional sense—it simply takes custom posts and templates and generates a static website—but I still call it one :).

It’s based on Python because it’s easy to modify and extend while remaining simple enough to fully understand.

## Building

Warning: You need Python ≥ 3.10 installed and available in your system PATH.

Build the site with:

```./lrcms build```

The generated site will be placed in the dist/ folder.

## Design

I chose a minimalist approach and removed anything that could feel unnecessary or distracting. The styling uses basic CSS, making it easy to edit and allowing me to switch designs with minimal effort.

## Posts

The system is designed to work with quick-to-write, Markdown-like files that are converted into HTML. Posts can include images, videos, and custom objects defined in asset files.

## Hosting

The site is hosted on Netlify, and the domain was purchased through Namecheap—nothing unusual. The site is automatically built and deployed on every Git push.