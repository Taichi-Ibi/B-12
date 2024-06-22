                                                                                                            
#!/bin/bash                                                                                                       
                                                                                                                    
# プロジェクト名の指定                                                                                            
PROJECT_NAME="B-12"                                                                                       
                                                                                                                    
# ディレクトリの作成                                                                                              
mkdir -p $PROJECT_NAME/$PROJECT_NAME                                                                              
mkdir -p $PROJECT_NAME/tests                                                                                      
mkdir -p $PROJECT_NAME/docs                                                                                       
                                                                                                                    
# ファイルの作成                                                                                                  
touch $PROJECT_NAME/$PROJECT_NAME/__init__.py                                                                     
touch $PROJECT_NAME/$PROJECT_NAME/main.py                                                                         
touch $PROJECT_NAME/$PROJECT_NAME/module.py                                                                       
                                                                                                                    
touch $PROJECT_NAME/tests/__init__.py                                                                             
touch $PROJECT_NAME/tests/test_module.py                                                                          
                                                                                                                    
touch $PROJECT_NAME/docs/index.md                                                                                 
                                                                                                                    
# .gitignoreの作成                                                                                                
cat <<EOL > $PROJECT_NAME/.gitignore                                                                              
__pycache__/                                                                                                      
*.pyc                                                                                                             
.env                                                                                                              
EOL                                                                                                               
                                                                                                                    
# README.mdの作成                                                                                                 
cat <<EOL > $PROJECT_NAME/README.md                                                                               
# $PROJECT_NAME                                                                                                   
                                                                                                                    
このプロジェクトの概要と使い方について説明します。                                                                
                                                                                                                    
## インストール                                                                                                   
                                                                                                                    
\`\`\`bash                                                                                                        
pip install -r requirements.txt                                                                                   
\`\`\`                                                                                                            
                                                                                                                    
## 使い方                                                                                                         
                                                                                                                    
\`\`\`bash                                                                                                        
python $PROJECT_NAME/main.py                                                                                      
\`\`\`                                                                                                            
EOL                                                                                                               
                                                                                                                    
# requirements.txtの作成                                                                                          
cat <<EOL > $PROJECT_NAME/requirements.txt                                                                        
numpy                                                                                                             
pandas                                                                                                            
EOL                                                                                                               
                                                                                                                    
# setup.pyの作成                                                                                                  
cat <<EOL > $PROJECT_NAME/setup.py                                                                                
from setuptools import setup, find_packages                                                                       
                                                                                                                    
setup(                                                                                                            
    name='$PROJECT_NAME',                                                                                         
    version='0.1',                                                                                                
    packages=find_packages(),                                                                                     
    install_requires=[                                                                                            
        'numpy',                                                                                                  
        'pandas',                                                                                                 
    ],                                                                                                            
)                                                                                                                 
EOL                                                                                                               
                                                                                                                    
echo "プロジェクト構造が作成されました。"          