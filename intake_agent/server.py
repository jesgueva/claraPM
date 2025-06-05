from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from intake_agent.controller import router as intake_router
from intake_agent.auth import (
    Token, User, authenticate_user, create_access_token, 
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES, users_db
)
from datetime import timedelta
from intake_agent.logger import system_logger

def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Clara Project Manager API", version="1.0.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # React app URL
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    
    # Include the intake agent router
    app.include_router(intake_router, prefix="/intake", tags=["intake"])
    
    @app.post("/token", response_model=Token)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        """Authenticate user and provide access token."""
        user = authenticate_user(users_db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        system_logger.info(f"User {user.username} logged in successfully")
        return {"access_token": access_token, "token_type": "bearer"}
    
    @app.get("/users/me", response_model=User)
    async def read_users_me(current_user: User = Depends(get_current_active_user)):
        """Get current user information."""
        system_logger.info(f"User {current_user.username} retrieved their profile")
        return current_user
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "Welcome to Clara PM API! See /docs for API documentation."}
    
    return app

app = create_app()

def run_server(host="0.0.0.0", port=8000):
    """Run the server."""
    import uvicorn
    system_logger.info(f"Starting Clara PM API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()