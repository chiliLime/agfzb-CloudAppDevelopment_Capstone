function main(params) {
    // console.log(params);
    return new Promise(function (resolve, reject) {
        const { CloudantV1 } = require('@ibm-cloud/cloudant');
        const { IamAuthenticator } = require('ibm-cloud-sdk-core');
        const authenticator = new IamAuthenticator({ apikey: "8ckBl7keNcWY0oanpzw95E0GKovlAq25M0PpMbGsZLAG" })
        const cloudant = CloudantV1.newInstance({
            authenticator: authenticator
        });
        cloudant.setServiceUrl("https://a3ed2682-49ec-4365-b98d-457a854d8086-bluemix.cloudantnosqldb.appdomain.cloud");
        if (params.id) {
            id = parseInt(params.id)
            // return reviews with this id
            cloudant.postFind({
              db: 'reviews',
              selector: {
                id: parseInt(params.id)
              }
            })
            .then((result)=>{
              // console.log(result.result.docs);
              let code = 200;
              if (result.result.docs.length == 0) {
                  code = 404;
              }
              resolve({
                  statusCode: code,
                  headers: { 'Content-Type': 'application/json' },
                  body: result.result.docs
              });
            }).catch((err)=>{
              reject(err);
            })
        } else {
            // return all documents 
            cloudant.postAllDocs({ db: 'reviews', includeDocs: true, limit: 10 })            
            .then((result)=>{
              // console.log(result.result.rows);
              let code = 200;
              if (result.result.rows.length == 0) {
                  code = 404;
              }
              resolve({
                  statusCode: code,
                  headers: { 'Content-Type': 'application/json' },
                  body: result.result.rows
              });
            }).catch((err)=>{
              reject(err);
            })
      }
    }
    )}