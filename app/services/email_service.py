import boto3

from app.config import settings


class EmailService:
    def __init__(self):
        self.client = boto3.client(
            "ses",
            endpoint_url=settings.aws.AWS_URL,
            aws_access_key_id=settings.aws.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.aws.AWS_SECRET_ACCESS_KEY,
            region_name=settings.aws.AWS_REGION_NAME,
        )

    async def send_reset_password_url(self, email, url) -> dict:
        response = self.client.send_email(
            Source="alexey.terleev@innowise-group.com",
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": "Reset Password"},
                "Body": {
                    "Html": {
                        "Charset": "UTF-8",
                        "Data": f'To reset yout password follow the link: <a class="ulink" href="{url}">Reset Password</a>.',
                    }
                },
            },
        )
        return response
