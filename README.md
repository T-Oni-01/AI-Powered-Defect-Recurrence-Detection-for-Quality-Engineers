# AI-Powered-Defect-Recurrence-Detection-for-Quality-Engineers

QE Defect AI is a desktop application that uses machine learning to help quality engineers identify recurring defects by analyzing historical repair records. It converts defect descriptions into semantic embeddings using state-of-the-art NLP models, enabling intelligent similarity matching based on meaning rather than just keywords.

<img width="959" height="539" alt="GUI New Defect Tab" src="https://github.com/user-attachments/assets/9679db7d-1f3d-4315-8804-b2ad588fbafd" />

***NOTE: SEE THE "PROJECT ARCHITECTURE" DOC FILE FOR A MORE DETAILED GUIDE***

Installer Setup: https://mega.nz/file/OEc1magb#KWCCcdYsOd6Le3loCbuQoQ8GGtgsRHGvkB4ti8vyjuo 

 Features:
* Semantic Similarity Search - Finds historically similar defects using sentence-transformers AI
* Recurrence Detection - Automatically flags recurring issues based on customizable thresholds
* Likely Solutions - Suggests most common resolutions from similar past defects with confidence percentages.
* The system uses a configurable threshold (default: 0.75) to determine recurrence:
  ≥ 0.75 - Likely recurring defect
  < 0.75 - Potentially new issue

  Installation:
  * Option 1: Windows Installer (Recommended)
    * Run the installer and follow the prompts
    * Launch from Start Menu
    * Note: Do move the data folder (that will contain the csv file of defect info) from the programs file to what readable folder location you want  (i.e. Documents).
    <img width="152" height="152" alt="image" src="https://github.com/user-attachments/assets/fadbd8dd-257b-4845-af43-9f87b6c0e2b8" />
* <img width="737" height="386" alt="image" src="https://github.com/user-attachments/assets/a59782b6-a83a-40fe-b059-6d71e37a0a54" />


    * Option 2: Run from Source
      * Python 3.8 or higher
      * pip package manager
     
  * Requirements.txt
    *PyQt6==6.5.0
    *pandas==2.0.3
    *openpyxl==3.1.2
    *sentence-transformers==2.2.2
     *scikit-learn==1.3.0
    *matplotlib==3.7.2
    *numpy==1.24.3
 
* <img width="959" height="539" alt="GUI Main Window" src="https://github.com/user-attachments/assets/784f3b29-4fd4-4a54-b302-9a35cb58e75d" />

* <img width="959" height="514" alt="Backend Build" src="https://github.com/user-attachments/assets/43151a30-2e9d-4448-ad59-67056ed177f3" />

*<img width="950" height="511" alt="GUI About" src="https://github.com/user-attachments/assets/2b88bfd5-b91e-4e64-87a3-704a85bbbc71" />

*<img width="959" height="511" alt="GUI Trend Tab" src="https://github.com/user-attachments/assets/2a6f8bcc-a3ac-4303-a231-9b80d3177c56" />



  
