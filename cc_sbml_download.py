from urllib.request import urlretrieve
import ccapi

#a simple function creating a permanent local file from the retrieved model file
def download_local(url, path, model_id, suffix='sbml'):
    filename = path+str(model_id)+'.'+suffix
    filename, _ = urlretrieve(url, filename=filename)
    return filename

def get_models():

    cc_email = "test@cellcollective.org"
    cc_password = "test"

    client = ccapi.Client()

    # raises AuthenticationError if login credentials are invalid
    client.auth(email=cc_email, password=cc_password)

    print(list(ccapi.constant.MODELS))
    #model = ccapi.load_model("lac-operon", client=client)

    # size = number of models to retrieve
    # since = starting from model # ...
    models = client.get("model", since=229, size=10)

    # model.default_type = type of the model
    counter = 0
    if models is None:
        print('not iterable')
    # print model name
    for model in models:
        counter += 1
        print(model.name)
    print(counter)