from bootstrap.api.app_factory import create_app

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app=create_app(), port=8000, host='0.0.0.0', reload=False, loop='uvloop')
