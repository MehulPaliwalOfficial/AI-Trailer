# GitHub Submission Steps

Follow these steps to submit the AI Movie Trailer Generator project on GitHub and paste the repository link in Google Forms.

## Method 1: Using GitHub Website

1. Download `AI_Movie_Trailer_Generator_Submission.zip` from Arena.
2. Extract/unzip it on your computer.
3. Go to https://github.com and sign in.
4. Click the `+` button in the top-right corner.
5. Click `New repository`.
6. Repository name: `AI-Movie-Trailer-Generator`
7. Description: `AI Movie Trailer Generator using Generative AI`
8. Choose `Public` unless your teacher asked for private.
9. Do **not** add README, .gitignore, or license on GitHub because the project already contains files.
10. Click `Create repository`.
11. On the new repository page, click `uploading an existing file`.
12. Open the extracted project folder on your computer.
13. Upload the project files/folders, especially:
    - `README.md`
    - `requirements.txt`
    - `.gitignore`
    - `src/`
    - `docs/`
    - `prompts/`
    - `sample_outputs/`
14. Scroll down and click `Commit changes`.
15. Copy your repository URL. It will look like:

```text
https://github.com/your-username/AI-Movie-Trailer-Generator
```

16. Paste this link in the Google Form.

## Method 2: Using Git Commands

After extracting the ZIP, open terminal/Git Bash inside the `AI_Movie_Trailer_Generator` folder and run:

```bash
git init
git add .
git commit -m "Initial commit - AI Movie Trailer Generator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AI-Movie-Trailer-Generator.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Important

- Submit the GitHub repository link, not the ZIP file link.
- Keep the repository public if the evaluator needs access.
- Open the repository link in an incognito/private window to confirm it is visible before pasting it in Google Forms.
