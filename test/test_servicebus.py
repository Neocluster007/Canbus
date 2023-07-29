import asyncio
from azure.servicebus.aio import ServiceBusClient

NAMESPACE_CONNECTION_STR = "Endpoint=sb://maas-iot.servicebus.windows.net/;SharedAccessKeyName=TunnelListener;SharedAccessKey=07wteQMxzwotmSbYlIzGuFINLgELDiUV7+ASbC0L8pc=;EntityPath=tunnel-trigger"
SUBSCRIPTION_NAME = "S1"
TOPIC_NAME = "tunnel-trigger"

async def run():
    # create a Service Bus client using the connection string
    async with ServiceBusClient.from_connection_string(
        conn_str=NAMESPACE_CONNECTION_STR,
        logging_enable=True) as servicebus_client:

        async with servicebus_client:
            # get the Subscription Receiver object for the subscription
            receiver = servicebus_client.get_subscription_receiver(topic_name=TOPIC_NAME, 
            subscription_name=SUBSCRIPTION_NAME, max_wait_time=5)
            async with receiver:
                received_msgs = await receiver.receive_messages(max_wait_time=5, max_message_count=20)
                for msg in received_msgs:
                    print("Received: " + str(msg))
                    # complete the message so that the message is removed from the subscription
                    await receiver.complete_message(msg)

while True:
    asyncio.run(run())