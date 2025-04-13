# Dota Auto Accept Script

## Setup and Compilation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11

### Installation Steps
1. Clone the repository or download the script
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

### Preparing Icon and Background Image
1. Create an icon for your application (optional)
   - Use tools like Photoshop, GIMP, or online icon converters
   - Recommended size: 256x256 pixels
   - Save as `.ico` format

2. Prepare the reference image (dota.png)
   - Capture a clear screenshot of the Dota 2 match accept button
   - Ensure high contrast and visibility

### Using the Compile Script (Recommended)
1. Ensure you have followed the installation steps and installed all prerequisites.
2. Navigate to the project directory in your terminal.
3. Run the compile script:
   ```batch
   .\compile-script.bat
   ```
   *(Note: Adjust the command if your script has a different name or extension, e.g., `compile-script.sh` for Linux/macOS)*
4. The compiled executable will be placed in the `dist` directory.

### WhatsApp API Integration
1. Prerequisites:
   - WhatsApp Business API account
   - API credentials (API key and secret)
   - Valid phone number for sending messages

2. Configuration:
   - Create a `.env` file in the project root with the following variables:
     ```
     WHATSAPP_API_KEY=your_api_key
     WHATSAPP_API_SECRET=your_api_secret
     WHATSAPP_PHONE_NUMBER=your_whatsapp_number
     ```

3. Sending Messages:
   - The script accepts the following parameters:
     - `--number`: Recipient's phone number (with country code, e.g., +5511999999999)
     - `--text`: Message content to send
     - `--password`: Your WhatsApp API password

   Example usage:
   ```bash
   python dota_auto_accept.py --number +5511999999999 --text "Your match is ready!" --password your_api_password
   ```

4. Security Notes:
   - Never share your API credentials
   - Keep your `.env` file secure and never commit it to version control
   - Use environment variables for sensitive data in production

### Troubleshooting
- Ensure all dependencies are installed
- Verify the reference image path is correct
- Check screen resolution compatibility