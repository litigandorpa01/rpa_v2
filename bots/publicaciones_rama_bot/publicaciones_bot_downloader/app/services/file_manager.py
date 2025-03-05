from app.services.downloader.download_factory import ProcessorFactory

class FileManager():
    def __init__(self,factory: ProcessorFactory):
        self.factory = factory
    
    async def process_file(self,file_name:str,file_url: str) -> str:
        
        if "my.sharepoint.com" in file_url:
            file_url=f"{file_url}&download=1"
        
        file_extension = await self.factory.get_file_type(file_url)
        
        processor = self.factory.create_processor(file_extension)

        if "text/html" in file_extension and "my.sharepoint.com" in file_url:
            file_url = file_url.replace("&download=1", "")
        
        return  await processor.download_file(file_name,file_url)