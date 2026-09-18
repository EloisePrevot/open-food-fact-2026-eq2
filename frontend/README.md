<a id="readme-top"></a>

# Frontend

### Technologies

- React 19 + TypeScript 6;
- Vite 8;
- [Mantine](https://mantine.dev/) 9 (components and theming) with [Lucide](https://lucide.dev/) icons;
- [React Router](https://reactrouter.com/) for navigation;
- [TanStack Query](https://tanstack.com/query/latest) for data fetching and caching;
- [React Hook Form](https://react-hook-form.com/) + [Zod](https://zod.dev/) for forms and validation;
- [Biome](https://biomejs.dev/) for formatting and linting;
- [Vitest](https://vitest.dev/) + [React Testing Library](https://testing-library.com/) for tests.

### Code structure

```text
src/
├── App.tsx                 # composition + routes (React Router)
├── main.tsx                # providers: Mantine, TanStack Query, Router
├── theme.ts                # Mantine theme
├── pages/                  # route-level pages
├── components/             # reusable components (AppHeader, ContactForm, ...)
├── apis/                   # HTTP access, one layer per resource
└── shared/                 # shared utilities (http) and test helpers
```


## Getting started

### Prerequisites

- Node.js 24 LTS;
- pnpm 11;
- the API running on `http://localhost:8080`.

### Installation

From the repository root:

```sh
pnpm install
```

## Usage

```sh
pnpm dev:frontend
```

Open `http://localhost:5173`. To work directly in this directory, `pnpm dev` produces the same result.

Scripts available in this directory:

```sh
pnpm check      # type checking (tsc)
pnpm lint:fix   # Resolve fixable lint + format issues
pnpm lint       # Biome (lint + format)
pnpm test       # Vitest (single run)
pnpm build      # production build into dist/
```