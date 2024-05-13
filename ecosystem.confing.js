module.exports = {
    apps: [
      {
        name: "zuperscore",
        script: "manage.py",
        args: "runserver 0.0.0.0:8000",
        instances: 1, // Number of instances to create
        autorestart: true, // Restart the app automatically if it crashes
        watch: true, // Watch for file changes and restart the app
        
      }
    ]
  };
  