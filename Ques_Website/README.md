# Ques Company Website

Official website for Shenzhen Ques Technology Co., Ltd - Building the OSINT Layer of AI Infrastructure.

## Overview

Modern, responsive single-page website with 4 main sections:
1. **About Us** - Company mission, vision, and OSINT AI infrastructure focus
2. **Our Products** - GeoSeer geolocation intelligence platform
3. **Our Team** - Leadership team profiles with social links
4. **Contact Us** - Email, phone, address, and social media

## Technology Stack

- **React 19.1.0** - UI framework
- **Vite 7.0.4** - Build tool and dev server
- **Tailwind CSS 4.1.17** - Utility-first CSS framework
- **Framer Motion 12.23.12** - Animation library
- **i18next 25.3.4** - Internationalization (English/Chinese)
- **React Icons 5.5.0** - Icon library

## Prerequisites

- Node.js 18.x or higher
- npm 9.x or higher

## Local Development

### Installation

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Access at: `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Output directory: `dist/`

### Preview Production Build

```bash
npm run preview
```

Access at: `http://localhost:4173`

## Deployment to CVM (Cloud Virtual Machine)

### Quick Deploy with Script (Recommended)

1. **Upload project to CVM**:
   ```bash
   # On your local machine
   scp -r /path/to/new/ user@your-server-ip:/home/user/ques-website
   ```

2. **Run deployment script**:
   ```bash
   # On your CVM
   cd /home/user/ques-website
   sudo ./deploy.sh
   ```

The script will:
- Check Node.js and npm installation
- Install/verify Nginx
- Install dependencies and build the project
- Deploy to `/var/www/ques`
- Configure Nginx with optimized settings
- Enable the site and restart Nginx
- Configure firewall rules

**Before running**: Edit `deploy.sh` and change `DOMAIN="your-domain.com"` to your actual domain.

### Manual Deployment

If you prefer manual deployment or need to customize the process:

### Step 1: Build the Project

```bash
npm run build
```

### Step 2: Upload to CVM

Upload the entire `dist/` folder to your CVM server.

### Step 3: Serve with Nginx

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

### Step 4: Serve with PM2 + Vite Preview (Alternative)

```bash
# Install PM2 globally
npm install -g pm2

# Start the preview server
pm2 start npm --name "ques-website" -- run preview

# Save PM2 process list
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

### Step 5: Configure Firewall

```bash
# Allow HTTP traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # For HTTPS

# Allow Vite preview port (if using PM2 method)
sudo ufw allow 4173/tcp
```

## Features

- **Bilingual Support**: Toggle between English (EN) and Chinese (CN)
- **Smooth Navigation**: Mouse wheel or swipe gestures to navigate sections
- **Responsive Design**: Optimized for desktop, tablet, and mobile
- **iOS Safe Area Support**: Handles notch screens properly
- **Scroll Control**: Threshold-based scrolling prevents accidental section skips
- **Team Social Links**: Click team member photos/names to visit their X (Twitter) profiles
- **Product Link**: GeoSeer logo and name link to https://geoseeer.com

## Navigation

- **Desktop**: Mouse wheel to scroll between sections (threshold-based)
- **Mobile**: Swipe up/down to navigate
- **Header**: Click navigation items to jump directly to sections
- **Language Toggle**: Switch in header (desktop) or mobile menu

## Project Structure

```
new/
├── public/
│   ├── geoseer-logo.png       # GeoSeer product logo
│   ├── police_logo.jpg        # Police registration logo
│   └── logo.ico               # Company favicon
├── src/
│   ├── assets/
│   │   ├── logo.ico           # Header logo
│   │   └── profile_pic/       # Team member photos
│   ├── components/
│   │   ├── AboutSection.jsx   # Company introduction
│   │   ├── ProductsSection.jsx # GeoSeer product showcase
│   │   ├── TeamSection.jsx    # Team profiles
│   │   ├── ContactSection.jsx # Contact information
│   │   ├── Header.jsx         # Navigation header
│   │   └── Footer.jsx         # Footer with legal info
│   ├── i18n/
│   │   ├── en.json            # English translations
│   │   └── cn.json            # Chinese translations
│   ├── utils/
│   │   ├── optimizeAnimation.js  # Animation optimization
│   │   └── viewportHeight.js     # Viewport height fix for mobile
│   ├── App.jsx                # Main app component
│   ├── main.jsx               # Entry point
│   ├── i18n.js                # i18n configuration
│   ├── index.css              # Global styles
│   └── viewportFix.css        # iOS viewport fixes
├── package.json
├── vite.config.js             # Vite configuration
├── tailwind.config.js         # Tailwind CSS configuration
└── postcss.config.js          # PostCSS configuration
```

## Configuration Files

### vite.config.js
- Configured to bind to `0.0.0.0` for CVM deployment
- Dev server: port 5173
- Preview server: port 4173

### tailwind.config.js
- Tailwind CSS v4 configuration
- Custom color palette based on blue gradient theme

### postcss.config.js
- Uses `@tailwindcss/postcss` plugin for Tailwind v4 compatibility

## Environment Requirements

### Development
- Node.js 18+
- Modern browser with ES6+ support

### Production (CVM)
- Linux-based server (Ubuntu/CentOS recommended)
- Nginx or similar web server
- OR PM2 for Node.js process management
- Firewall configured for HTTP/HTTPS

## Contact

**Email**: cody@quesx.com  
**Phone**: +86 (755) 26400640  
**Address**: Floor 20, Tower A, Phoenix City, Guangming District, Shenzhen, Guangdong Province

## Social Media

- X (Twitter): [@GeoSeeer](https://x.com/GeoSeeer)
- Instagram: [@geoseeer](https://www.instagram.com/geoseeer/)
- TikTok: [@geoseeer](https://www.tiktok.com/@geoseeer)
- Facebook: [GeoSeer](https://www.facebook.com/profile.php?id=61583773556872)
- YouTube: [@geoseeer](https://www.youtube.com/@geoseeer)
- LinkedIn: [company/geoseer](https://www.linkedin.com/company/geoseer)

## License

© 2025 Shenzhen Ques Technology Co., Ltd. All rights reserved.
