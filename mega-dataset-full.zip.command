@echo off
echo Creating zip...
cd "C:\Users\PC1\Desktop\dental-ai"
del mega-dataset-upload.zip 2>nul
"C:\Program Files\7-Zip\7z.exe" a -tzip mega-dataset-upload.zip mega-dataset\* 2>nul || tar -czf mega-dataset-upload.tar.gz mega-dataset
echo Done.
dir mega-dataset-upload.* 2>nul
