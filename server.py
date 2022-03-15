# Reference: https://fedoramagazine.org/create-containerized-machine-learning-model/

import connexion

app = connexion.App(__name__, specification_dir='./')

app.add_api('openapi.yaml')

if __name__ == '__main__':
    app.run(debug=True)