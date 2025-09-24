

##### backend

### 1. **Navigate to your project backend folder:


cd backend

#### 2. **Create a virtual environment** (if you don’t already have one):


python3 -m venv venv (it could be created already)

#### 3. **Activate the virtual environment**:

## * macOS / Linux:


source venv/bin/activate

### * Windows:

venv\Scripts\activate

### 4. **Install your packages inside the venv**:

pip install --upgrade pip

### pip install fastapi[all] boto3 python-dotenv

### pip install "fastapi[all]"
### pip install fastapi\[all\]

pip install "fastapi[all]" boto3 python-dotenv


### if there was a problem, you need to either quote the package name or escape the brackets

### 5. **Run your FastAPI server**:

### uvicorn main:app --reload

uvicorn main:app --reload --host 0.0.0.0 --port 8000

### front end

### In Next.js, sometimes you need to clear cache to avoid stale builds, environment variable issues, or corrupted .next files. Here’s how to do it:

# Navigate to your frontend root
cd frontend

# Remove Next.js build cache
rm -rf .next

# (Optional but recommended) Remove node_modules and lock file
rm -rf node_modules package-lock.json

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
npm install

# Start Next.js dev server
npm run dev

### Tip: You can combine the first four steps in one line if you want a really fast “reset”:

rm -rf .next node_modules package-lock.json && npm cache clean --force && npm install && npm run dev


### ✅ This ensures all caches are cleared and you’re running the latest code with fresh dependencies.





