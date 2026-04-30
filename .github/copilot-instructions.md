This is a comprehensive set of rules. I've organized them into a structured `.github/copilot-instructions.md` file. This format ensures Copilot understands the hierarchy of your project, from file naming to specific React architectural patterns.

---

## `.github/copilot-instructions.md`

### **General Principles**

- **Simplicity First:** Write code that is as easy to read as a book. Avoid overly complicated solutions.
- **File Naming:** Use `kebab-case` for all files and folders.
- **TypeScript:** Use TypeScript strictly. Do not use `any` or other workarounds.
- **Styling:** Use **Tailwind CSS** exclusively. Do not use inline CSS or external stylesheets.

---

### **React Architecture**

- **Logic Separation:** Keep components "dumb." Move all logic, state handling, and API calls into **custom hooks**.
- **Component Size:** Keep components small and modular. Maximum length: **150-180 lines**.
- **State Management:** Use Zustand for global state management. Avoid prop drilling and context unless necessary.
- **Exports:** Always use Named Exports.

✅ export const MyComponent = ...

❌ export default MyComponent

---

### Project Architecture

This project uses a feature-colocated architecture within the Next.js App Router. Features are grouped by route, while shared resources live at the root.

Core Folder Structure:

/app
├── (auth)/
│ └── signup/
│ ├── page.tsx
│ ├── components/ // Feature-specific UI
│ ├── hooks/ // Feature-specific logic
│ └── utils/ // Feature-specific helpers
├── dashboard/
│ ├── voice-console/
│ │ ├── page.tsx
│ │ └── components/
│ └── settings/
│ ├── page.tsx
│ └── components/
/components
├── ui/ // shadcn/ui components
└── forms/ // Reusable form patterns
/hooks // Shared global hooks
/utils // Shared global utilities
/lib // API clients, configs, and shared helpers
/types // Global TypeScript definitions

---

### **Naming Conventions**

#### **Booleans**

Use positive naming. Avoid negative logic (e.g., "no", "not", "dis").

- ✅ `isEnabled`, `isActive`, `hasBillingAddress`
- ❌ `isDisabled`, `isNotActive`, `hasNoBillingAddress`

#### **Functions & Handlers**

- **Internal Handlers:** Use the `handle` prefix (e.g., `handleFormSubmit`, `handleResetPassword`).
- **Component Props:** Use the `on` prefix (e.g., `onFormSubmit`, `onNameChange`).
- **General Helpers:** Use descriptive verbs like `format`, `convert`, `normalize`, `transform`, `get`, or `set`.
  - ✅ `formatCurrencyAmount`, `normalizePhoneNumber`, `getUserToken`
  - ❌ `process`, `calc`, `calculateTotalPriceForAllItemsInCart...` (Too long or vague)

#### **Example Pattern**

```tsx
<SomeComponent onNameChange={handleNameChange} onFormReset={handleFormReset} />
```
