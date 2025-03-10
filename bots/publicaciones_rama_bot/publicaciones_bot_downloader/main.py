import asyncio

from app.services.rabbitmq.consumer import RabbitMQConsumer
        
async def main():    
    consumer = RabbitMQConsumer()
    await consumer.connect()
    await consumer.start_consuming()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupción manual del programa.")

