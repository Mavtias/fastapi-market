from fastapi import FastAPI, Request, Depends                            # , Body, Response, status, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles 
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .routers import user, account, ad, misc
from . import auth, schemas, database, models, oauth2, middleware



app = FastAPI()


app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")

templates = Jinja2Templates(directory = "app/templates")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(
#     middleware.AuthMiddleware)


"""
_______________________________________________________________________________________________________
                                                Routes                              
_______________________________________________________________________________________________________
"""




app.include_router(account.router)
app.include_router(misc.router)
app.include_router(ad.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, 
                db: Session = Depends(database.get_db),
                user: models.User = Depends(oauth2.get_optional_user)):
    
    categories_counts = {
        "vehicles": db.query(models.Product).filter(models.Product.category == "vehicles").count(),
        "real_estate": db.query(models.Product).filter(models.Product.category == "real estate").count(),
        "mobiles": db.query(models.Product).filter(models.Product.category == "mobiles").count(),
        "electronics": db.query(models.Product).filter(models.Product.category == "electronics").count(),
    }
    total_ads = db.query(models.Product).count()
    total_users = db.query(models.User).count()
    total_locations = db.query(models.User.country).distinct().count()
    latest_products = db.query(models.Product).join(models.User).order_by(models.Product.created_at.desc()).limit(6).all()
    
    
    return templates.TemplateResponse("index.html", {"request": request, 
                                                     "products": latest_products,
                                                     "categories_counts": categories_counts,
                                                     "ads": total_ads,
                                                     "locations":total_locations,
                                                     "users": total_users,
                                                     "user": user})


