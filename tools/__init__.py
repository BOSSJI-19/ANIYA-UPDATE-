from .play import register_handlers as register_play_handlers

def setup_tools(app):
    """
    Saare tools ke handlers ko yahan register karenge.
    """
    # Play aur Stop commands register karo
    register_play_handlers(app)
    
    print("✅ Tools Loaded: Play & Stop System")
  
