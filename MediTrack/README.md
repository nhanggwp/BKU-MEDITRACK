## Name conventions

### 1. **Folder and File Names**

- Use **camelCase** or **kebab-case** for folders and filenames.
  - Examples:
    - `components/` (folder)
    - `userProfile.js` (file)
- For React components, use **PascalCase** filenames.
  - Example: `LoginForm.js`, `UserProfile.js`

### 2. **Variables and Functions**

- Use **camelCase**.
  - Examples:
    - `userName`
    - `handleSubmit`
- Function only used in 1 file (helper function) starts with '\_'

### 3. **Main Components of File**

- Same as filename.
- Examples:
  - `LoginForm.js` --> `const LoginForm = () => {...}`

## Folder Structure

### 1. ClientApp/

- `src/`: source folder containing code of every tab, also some helpers, util...:
  - `components/`: components used across project (button, input box,...).
  - `GlobalStyle.js`: css layout used across project (color, text font, ...).
- `assets/`: imgs used across project (logo,...)

### 2. Model/

- For AI algorithms (empty now)

### 3. App.js

- Acts just like the `main()` in C++
- Renders every tab and controls switching between them.

## File Structure for Coding Tabs

1.  `import`: library section.
2.  `const <filename>`: main component. Don't use inline css, instead, define it in `styles`.
3.  `styles`: holds every custom layout used for the file (or the tab) only. E.g: padding, margin, width, height,...
4.  `export`: export section.

## How To Run

1. `npm install`: do once to install all required libraries.
2. `npm start`
3. Run the virtual android/ios interface in Android Studio on desktop or scan the QR code via app `Expo Go` on CHPlay/Appstore on your mobile phone.
