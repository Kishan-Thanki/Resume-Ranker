from app.database import Base, engine

# These classes are imported into memory, So their metadata is registered.
from app.models import Resume, Job_Description

# Create all registered table if didn't exists.
Base.metadata.create_all(bind=engine)