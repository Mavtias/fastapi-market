import os
import shutil
import uuid
from PIL import Image

from fastapi import Depends, APIRouter, Request, Form, UploadFile, File, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List

from .. import models, schemas, utils, oauth2, database
from ..database import get_db



#templates = Jinja2Templates(directory = "../templates")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))
router = APIRouter(
    prefix = "/ad",
    tags = ['Ads']
)


@router.get("/list", response_class=HTMLResponse)
async def adlistinglist(request: Request, db: Session = Depends(get_db), user: models.User = Depends(oauth2.get_optional_user)):

    products = db.query(models.Product).all()

    return templates.TemplateResponse("adlistinglist.html", {"request": request, "products": products})

@router.get("/category", response_class=HTMLResponse)
async def category(
    request: Request, 
    db: Session = Depends(get_db), 
    user: models.User = Depends(oauth2.get_optional_user), 
    category: str = None, 
    search_query: str = None,  # Añadimos la búsqueda por nombre o país
    country: str = None,
    page: int = 1,
    page_size: int = 10
):
    if search_query == 'None':
        search_query = ''

    # Conteo de productos por categoría
    category_counts = {
        "vehicles": db.query(models.Product).filter(models.Product.category == "vehicles").count(),
        "real estate": db.query(models.Product).filter(models.Product.category == "real estate").count(),
        "mobiles": db.query(models.Product).filter(models.Product.category == "mobiles").count(),
        "electronics": db.query(models.Product).filter(models.Product.category == "electronics").count(),
    }

    # Construir la query base para productos
    query = db.query(models.Product)

    # Filtrar por categoría si está presente
    if category:
        query = query.filter(models.Product.category == category)

    # Filtrar por búsqueda si hay un query de búsqueda
    if search_query:
        query = query.filter(models.Product.title.ilike(f"%{search_query}%"))
    
   
    # Filtrar por país si se seleccionó uno
    if country:
        query = query.join(models.User).filter(models.User.country == country)

    # Total productos
    total_products = query.count()

    offset = (page - 1) * page_size

    # Obtener los últimos 10 productos filtrados
    products = query.order_by(models.Product.created_at.desc())\
        .offset(offset)\
        .limit(page_size)\
        .all()
    
    total_pages = (total_products + page_size - 1) // page_size

    no_results_error = None
    if not products:
        no_results_error = "No products found matching your criteria, maybe try with other keywords or in another category / country?"

    # Renderizar la plantilla
    return templates.TemplateResponse("category.html", {
        "request": request,
        "user": user,
        "products": products,  
        "category_counts": category_counts,  # Pasar el conteo de productos por categoría
        "selected_category": category,
        "search_query": search_query if search_query is not None else '',  # Para mantener el valor en el campo de búsqueda si se utilizó
        "country": country,
        "no_results_error": no_results_error,
        "total_products": total_products,
        "total_pages": total_pages,
        "page": page
    })


@router.get("/product/{product_id}", response_class=HTMLResponse)
async def ads_details(
        request: Request,
        product_id: int,
        db: Session = Depends(get_db), 
        user: models.User = Depends(oauth2.get_optional_user)):
    
    product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if not product:
        return RedirectResponse(url=request.url_for('not_found'))

    return templates.TemplateResponse("ads-details.html", {"request": request, 
                                                           "user":user,
                                                           "product": product})


@router.get("/post-ad", response_class=HTMLResponse)
async def post_ads(request: Request, current_user: models.User = Depends(oauth2.get_current_user)):
    print(current_user)
    return templates.TemplateResponse("post-ads.html", {"request": request, "user": current_user})


@router.post("/post-ad", response_class=HTMLResponse)
async def post_ads(
    request: Request,
    title: str = Form(...),
    category: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    files: List[UploadFile] = File(None),
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db)):

    upload_folder = "app/assets/img/uploads/"
    os.makedirs(upload_folder, exist_ok=True)
    image_urls = []   #image_url = None

    target_size = (800, 800)

    if files:
        for file in files:
            if file.filename:
                file_extension = os.path.splitext(file.filename)[1]
                file_name = f"{uuid.uuid4()}{file_extension}"  # Usar UUID para evitar conflictos de nombres
                image_path = os.path.join(upload_folder, file_name)
                 # Asegúrate de obtener el nombre del archivo y construir la ruta completa

                try:
                    image = Image.open(file.file)
                    image.thumbnail(target_size)
                    image.save(image_path, optimize=True, quality=85)
                    image_urls.append(f"/assets/img/uploads/{file_name}")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
                #     ###
                #     with open(image_path, "wb") as buffer:
                #         shutil.copyfileobj(file.file, buffer)
                #     image_urls.append(f"/assets/img/uploads/{file_name}")  # La URL pública para acceder a la imagen antigua image_url = f"/assets/img/uploads/{file_name}"
                # except Exception as e:
                #     raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
            
    if not image_urls:
        image_urls.append("/assets/img/no-image.png")

    image_urls_str = ','.join(image_urls)

    new_product = models.Product(
        title = title,
        category = category,
        price=price,
        description = description,
        image_url = image_urls_str,
        owner_id = current_user.id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return RedirectResponse(url="/account/dashboard", status_code=status.HTTP_302_FOUND)

