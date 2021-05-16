function getUserInfo(token, callback) {
    fetch("../api/getuserinfo", {
        method: 'POST',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
                token: token
            }
        )
    }).then(res => {
            return res.json()
        }
    ).then(res => {
        (res.msg)
        if (res.code === '0') {
            return res.data
        }
        layer.msg("用户信息获取失败")
    }).then(callback)
}


function SVGToImage(settings) {
    let _settings = {
        svg: null,
        // Usually all SVG have transparency, so PNG is the way to go by default
        mimetype: "image/png",
        quality: 0.92,
        width: "auto",
        height: "auto",
        outputFormat: "base64"
    };

    // Override default settings
    for (let key in settings) {
        _settings[key] = settings[key];
    }

    return new Promise(function (resolve, reject) {
        let svgNode;

        // Create SVG Node if a plain string has been provided
        if (typeof (_settings.svg) == "string") {
            // Create a non-visible node to render the SVG string
            let SVGContainer = document.createElement("div");
            SVGContainer.style.display = "none";
            SVGContainer.innerHTML = _settings.svg;
            svgNode = SVGContainer.firstElementChild;
        } else {
            svgNode = _settings.svg;
        }

        let canvas = document.createElement('canvas');
        let context = canvas.getContext('2d');

        let svgXml = new XMLSerializer().serializeToString(svgNode);
        let svgBase64 = "data:image/svg+xml;base64," + btoa(svgXml);

        const image = new Image();

        image.onload = function () {
            let finalWidth, finalHeight;

            // Calculate width if set to auto and the height is specified (to preserve aspect ratio)
            if (_settings.width === "auto" && _settings.height !== "auto") {
                finalWidth = (this.width / this.height) * _settings.height;
                // Use image original width
            } else if (_settings.width === "auto") {
                finalWidth = this.naturalWidth;
                // Use custom width
            } else {
                finalWidth = _settings.width;
            }

            // Calculate height if set to auto and the width is specified (to preserve aspect ratio)
            if (_settings.height === "auto" && _settings.width !== "auto") {
                finalHeight = (this.height / this.width) * _settings.width;
                // Use image original height
            } else if (_settings.height === "auto") {
                finalHeight = this.naturalHeight;
                // Use custom height
            } else {
                finalHeight = _settings.height;
            }

            // Define the canvas intrinsic size
            canvas.width = finalWidth;
            canvas.height = finalHeight;

            // Render image in the canvas
            context.drawImage(this, 0, 0, finalWidth, finalHeight);

            if (_settings.outputFormat == "blob") {
                // Fullfil and Return the Blob image
                canvas.toBlob(function (blob) {
                    resolve(blob);
                }, _settings.mimetype, _settings.quality);
            } else {
                // Fullfil and Return the Base64 image
                resolve(canvas.toDataURL(_settings.mimetype, _settings.quality));
            }
        };

        // Load the SVG in Base64 to the image
        image.src = svgBase64;
    });
}


function getarandomImage(seed) {
    seededRandom = function (max, min, seed) {
        max = max || 1;
        min = min || 0;

        seed = (seed * 9301 + 49297) % 233280;
        var rnd = seed / 233280.0;

        return min + rnd * (max - min);   // Math.ceil实现取整功能，可以根据需要取消取整
    }

    let cloths = Object.keys(Avataaars.paths.clothing)
    const cloth = cloths[Math.floor(seededRandom(1, 0, seed) * cloths.length)];
    let eyes = Object.keys(Avataaars.paths.eyes)
    const eye = eyes[Math.floor(seededRandom(1, 0, seed + 1) * eyes.length)];
    let tops = Object.keys(Avataaars.paths.top)
    const top = tops[Math.floor(seededRandom(1, 0, seed + 2) * tops.length)];
    let skin_colors = Object.keys(Avataaars.colors.skin)
    const skin = skin_colors[Math.floor(seededRandom(1, 0, seed + 3) * skin_colors.length)];
    let hair_colors = Object.keys(Avataaars.colors.hair)
    const hair_color = hair_colors[Math.floor(seededRandom(1, 0, seed + 4) * hair_colors.length)];
    const clothingGraphics = Object.keys(Avataaars.paths.clothingGraphic)
    const clothingGraphic = clothingGraphics[Math.floor(seededRandom(1, 0, seed + 5) * clothingGraphics.length)];
    const accessories = Object.keys(Avataaars.paths.accessories)
    const accessorie = accessories[Math.floor(seededRandom(1, 0, seed + 6) * accessories.length)];

    const svg = Avataaars.create({
        eyes: eye,
        clothing: cloth,
        hairColor: hair_color,
        clothingGraphic:clothingGraphic,
        skin:skin,
        top:top,
        accessories:accessorie
    });

    return SVGToImage({
        svg: svg,
        mimetype: "image/png",
        width: 140,
        height: 140,
        quality: 1,
        outputFormat: "base64"
    }).then(function (outputData) {
        return outputData
    }).catch(function (err) {
        console.log(err);
    })
}
