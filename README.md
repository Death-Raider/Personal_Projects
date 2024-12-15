# Self-Hosted Database Project  

This project is a lightweight solution for creating and managing a **self-hosted local database** using the `nedb` package. It serves as an entry-level project to learn how to handle databases, manage server-side storage, and implement caching mechanisms for web applications.

---

## Key Features  

1. **Local Database with `nedb`**  
   - Utilizes `nedb` to create and manage a lightweight, self-hosted database stored locally as `database.db`.  

2. **User Interaction**  
   - The application collects:  
     - **User Location** (requires location permissions).  
     - **Mood Input** (submitted as text).  

3. **Data Storage**  
   - Stores the user's location and mood into the database for quick, local access.  

4. **History Display**  
   - Provides an additional page (`all.html`) to display the history of user inputs stored in the database.  

5. **Server-Side Caching**  
   - Implements local server-side storage to enable caching and reduce load times for frequently accessed data.  

---

## Project Structure  

```
Self-Hosted-Database/  
├── public/  
│   ├── all.html             # Displays the history of user inputs from the database  
│   └── index.html           # Main page for collecting user input  
├── database.db              # Local database file managed by nedb  
├── package-lock.json        # Dependency lock file  
├── package.json             # Node.js project configuration file  
├── server.js                # Backend server script for handling requests and database operations  
├── Procfile                 # For deployment configuration (e.g., Heroku)  
└── README.md                # Documentation (this file)  
```  

---

## How It Works  

1. **Data Collection**  
   - Users visit `index.html` where they can enter their mood.  
   - Upon submission, the website requests location permissions to capture the user's location.  
   - Both the mood and location are sent to the server and stored in `database.db`.  

2. **Data Retrieval**  
   - Users can navigate to `all.html` to view a history of all submitted inputs stored in the database.  
   - The server fetches the data from `database.db` and sends it back to the front end for display.  

3. **Caching**  
   - Frequently accessed data is cached locally on the server to optimize performance.  

---

## Installation  

### Prerequisites  
1. Node.js installed on your system.  

### Steps  

1. Install dependencies:  
   ```bash  
   npm install  
   ```  

2. Start the server:  
   ```bash  
   node server.js  
   ```  

3. Open the application in your browser:  
   - Main page: `http://localhost:3000`  
   - History page: `http://localhost:3000/all.html`  

---

## Example Flow  

1. **On the Main Page (`index.html`)**:  
   - Enter your mood (e.g., "Happy").  
   - Allow location permissions.  
   - Click **Submit** to store the data in the local database.  

2. **On the History Page (`all.html`)**:  
   - View the list of all submitted moods and locations.  

---

## Dependencies  

1. **Node.js Packages**  
   - `nedb`: For lightweight database management.  
   - `express`: For setting up the server and handling HTTP requests.  
   - `body-parser`: For parsing incoming request bodies.  

---

## Future Improvements  

1. **Enhance UI**  
   - Add a user-friendly interface for better interaction.  
2. **Data Export**  
   - Allow users to export the history as a CSV or JSON file.  
3. **Add Authentication**  
   - Implement user accounts for personalized histories.  
4. **Cloud Integration**  
   - Provide an option to sync the local database with cloud storage for backup.  

---

## Learning Goals  

This project helped in understanding:  
1. Quick and efficient database management with `nedb`.  
2. Handling user permissions and input.  
3. Setting up a basic server for local storage and caching.  
4. Designing simple client-server interactions.  

---

Feel free to fork and contribute to this project! 😊