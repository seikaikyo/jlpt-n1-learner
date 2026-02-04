module.exports = {
  apps: [
    {
      name: 'jlpt-n1-frontend',
      cwd: '/Users/dash/Documents/github/jlpt-n1-learner/frontend',
      script: 'npm',
      args: 'run dev',
      env: {
        PORT: 5172
      },
      watch: false,
      autorestart: false
    },
    {
      name: 'jlpt-n1-backend',
      cwd: '/Users/dash/Documents/github/jlpt-n1-learner/backend',
      script: './venv/bin/uvicorn',
      args: 'app.main:app --port 8002 --host 127.0.0.1',
      interpreter: 'none',
      watch: false,
      autorestart: false
    }
  ]
}
