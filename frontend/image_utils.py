import os, requests, base64
from access_key import aws_config
import boto3
from botocore.config import Config
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}

my_config = Config(
    region_name = 'us-east-1',
    #signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

s3=boto3.client('s3', config=my_config, aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])

def upload_image(request, key):
    img_url = request.form.get('img_url')
    if img_url == "":
        file = request.files['file']
        _, extension = os.path.splitext(file.filename)
        if extension.lower() in ALLOWED_EXTENSIONS:
            try:
                print("trying")
                base64_image = base64.b64encode(file.read())

                s3.put_object(Body=base64_image,Key=key,Bucket="image-bucket-a3",ContentType='image')
                print("uploaded")
                return "VALID"
            except:
                return "INVALID"
            # return "SAVED"
        return "INVALID"

    response = requests.get(img_url)
    if response.status_code == 200:
        _, extension = os.path.splitext(img_url)
        if extension.lower() in ALLOWED_EXTENSIONS:
            filename = key + extension
            base64_image = base64.b64encode(response.content)
            s3.put_object(Body=base64_image,Key=key,Bucket="image-bucket-a3",ContentType='image')
            return "VALID"
            # try:
            #     return write_img_db(key, key)
            # except:
            #     return "INVALID"
    return "INVALID"

# def write_img_db(image_key, image_tag):
#     """ Write image to DB

#         Parameters:
#             image_key (int): key value
#             image_tag (str): file name

#         Return:
#             response (str): "OK" or "ERROR"
#     """
#     if image_key == "" or image_tag == "":
#         error_msg="FAILURE"
#         return error_msg
#     try:
#         cnx = get_db()
#         cursor = cnx.cursor(buffered = True)
#         query_exists = "SELECT EXISTS(SELECT 1 FROM image_table WHERE image_key = (%s))"
#         cursor.execute(query_exists,(image_key,))
#         for elem in cursor:
#             if elem[0] == 1:
#                 query_remove = '''DELETE FROM image_table WHERE image_key=%s'''
#                 cursor.execute(query_remove,(image_key,))
#                 break

#         query_add = ''' INSERT INTO image_table (image_key,image_tag) VALUES (%s,%s)'''
#         cursor.execute(query_add,(image_key,image_tag))
#         cnx.commit()
#         cnx.close()
#         return "OK"
#     except:
#         return "FAILURE"
