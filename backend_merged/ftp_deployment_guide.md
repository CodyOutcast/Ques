# 📁 FTP/SFTP Deployment Guide
# Use these GUI tools if SSH command line doesn't work

## Windows Tools:
1. **WinSCP** (Recommended)
   - Download: https://winscp.net/
   - Host: 172.16.0.16
   - Port: 22 (or try 2222, 22222)
   - Username: root
   - Password: [your server password]

2. **FileZilla**
   - Download: https://filezilla-project.org/
   - Use SFTP protocol
   - Host: sftp://172.16.0.16

3. **Visual Studio Code with SFTP Extension**
   - Install "SFTP" extension
   - Configure connection to your server

## Upload Process:
1. Connect to your server using any tool above
2. Navigate to /opt/ques-backend/ on the server
3. Upload contents of deployment_package folder
4. Use the web console to run migration commands

## If Port 22 doesn't work, try:
- Port 2222 (common alternative)
- Port 22222 (another alternative)
- Check with your hosting provider for the correct SSH port
