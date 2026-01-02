# Smart Eye Dashboard Frontend

React + Vite interface for the Smart Eye surveillance and reminder platform.

## Getting Started

```sh
cd frontend
npm install
npm run dev
```

The app listens on http://localhost:5173 and expects the FastAPI backend at http://127.0.0.1:8000.

## Available Scripts

- npm run dev – start the development server with hot reload
- npm run build – create an optimized production build
- npm run build:dev – produce a development-mode bundle for debugging
- npm run preview – preview the production build locally
- npm run lint – lint the project with ESLint

## Tech Stack

- React 18 with TypeScript
- Vite build tooling
- Tailwind CSS and shadcn/ui component library
- TanStack Query for data fetching and caching

## Project Structure

- src/pages – high level routes such as Dashboard, Alerts, Enroll, and Settings
- src/components – shared UI primitives and layout components
- src/contexts – global providers for authentication and theming
- src/lib – API helpers and utilities

## Deployment Notes

1. Run npm run build to produce assets in dist
2. Serve the dist directory with your preferred static hosting solution
3. Configure environment variables or proxy rules as needed to reach the backend API
