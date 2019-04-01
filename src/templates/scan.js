function scanToJpg() {
            scanner.scan(displayImagesOnPage,
            {
                "output_settings" :
                [
                    {
                        "type" : "return-base64",
                        "format" : "jpg"
                    }
                ]
            });
        }
        /** Processes the scan result */
        function displayImagesOnPage(successful, mesg, response) {
        if(!successful) { // On error
            console.error('Failed: ' + mesg);
            return;
        }

        if(successful && mesg != null && mesg.toLowerCase().indexOf('user cancel') >= 0) { // User canceled.
            console.info('User canceled');
            return;
        }

        var scannedImages = scanner.getScannedImages(response, true, false); // returns an array of ScannedImage
        for(var i = 0; (scannedImages instanceof Array) && i < scannedImages.length; i++) {
            var scannedImage = scannedImages[i];
            processScannedImage(scannedImage);
        }
        }

        /** Images scanned so far. */
        var imagesScanned = [];

        /** Processes a ScannedImage */
        function processScannedImage(scannedImage) {
        imagesScanned.push(scannedImage);
        var elementImg = createDomElementFromModel( {
            'name': 'img',
            'attributes': {
                'class': 'scanned',
                'src': scannedImage.src
            }
        });
        document.getElementById('images').appendChild(elementImg);
        }
