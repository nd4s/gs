import os
import requests
import csv
from jinja2 import Template
import time
import hashlib
import qrcode
from datetime import datetime

def get_google_sheet(spreadsheet_id, out_dir):
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv'
    response = requests.get(url)
    if response.status_code == 200:
        filepath = os.path.join(out_dir, 'test.csv')
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return filepath
    else:
        raise ValueError(f'Google Таблицю не скачано! Зверніться до адміністратора. Код: {response.status_code}')

def download_image(url, output_dir):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            image_filename = os.path.basename(url)
            image_path = os.path.join(output_dir, image_filename)
            with open(image_path, 'wb') as f:
                f.write(response.content)
            return image_filename
        else:
            print(f"Картинку не скачано! Користуйтеся i.ibb.co, інакше зверніться до адміністратора. Код: {response.status_code}")
            return None
    except Exception as e:
        print(f"Опис помилки, яка сталася при скачуванні картинки: {str(e)}")
        return None

def generate_html_from_csv(csv_filepath, output_dir):
    with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        rows = [row for row in reader]
    total_rows = len(rows)
    my_tags = []
    tag_descriptions = {}
    tag_bottom_descriptions = {}  # New dictionary for column 5
    qr_codes = {}
    urls = {}
    images = {}
    edition_date = datetime.now().strftime("%d.%m.%Y, %H:%M")
    for index, row in enumerate(rows):
        my_tags.append(row[0])
        tag_descriptions[row[0]] = row[4]
        tag_bottom_descriptions[row[0]] = row[5]  # Add column 5 data
        qr_codes[row[0]] = generate_qr_code(row[7], output_dir)
        urls[row[0]] = row[7]
        images[row[0]] = download_image(row[2], output_dir)
        print(f"Опрацьовується рядок {index + 1} із {total_rows}.\nЛишилося рядків - {total_rows - (index + 1)}.\n")

    template_string = """
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Хмара можливостей</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@100..900&display=swap');
        html {
            font-family: 'Montserrat', sans-serif;
            height: 100%;
            margin: 0;
        }
        body {
            display: flex;
            flex-direction: column;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .edition-banner {
            position: absolute;
            top: 20px;
            left: 20px;
            width: 250px;
            height: 50px;
            background-color: #b80000;
            color: white;
            opacity: 0.9;
            border-radius: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-family: 'Montserrat', sans-serif;
        }
        .pdf-download {
            position: absolute;
            top: 80px;
            left: 20px;
            width: 250px;
            height: 85px;
            background-color: black;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            border-radius: 25px;
        }
        .content-container {
            display: flex;
            flex: 1;
            margin: 0 2.5vw;
            align-items: stretch;
            box-sizing: border-box;
        }
        .tagcloud {
            flex: 1;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            position: relative;
            overflow: visible;
            min-height: 80vh;
            transition: opacity 0.3s ease; /* Transition for opacity */
        }
        .description {
            width: 50%;
            height: 80%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 10px;
            box-sizing: border-box;
        }
        .description-top {
            white-space: pre-wrap;
            flex-grow: 1;
            overflow: auto;
            font-size: 200%;
        }
        .description-bottom {
            background-color: #bae1ff;
            height: 20%;
            border-radius: 30px;
            border: 5px dashed #b80000;
            display: none; /* Initially hidden */
            white-space: pre-wrap;
            overflow: auto;
            font-size: 150%; 
            font-weight: bold; /* Bold text */
            text-align: center; /* Center aligned */
            padding: 20px; 
}

        .footer {
            width: 100%;
            height: 20%;
            background-color: lightgrey;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2%;
            box-sizing: border-box;
            position: fixed;
            bottom: 0;
        }
        .footer input {
            width: calc(50% - 100px);
            height: 50%;
            margin-right: 10px;
            border-radius: 50px;
            font-family: 'Montserrat', sans-serif;
            font-size: 150%;
            padding: 10px;
            box-sizing: border-box;
        }
        .dropdown {
            white-space: nowrap;
            position: absolute;
            background: white;
            border: 1px solid #ccc;
            z-index: 10;
            max-height: 50vh;
            overflow-y: auto; /* Allow scrolling */
            width: calc(50% - 100px);
            font-size: 150%;
            font-family: 'Montserrat', sans-serif;
            display: none;
            bottom: 90%;
            border-radius: 50px;
            box-sizing: border-box;
        }
        .dropdown::-webkit-scrollbar {
            width: 0; 
            background: transparent; 
        }
        .dropdown {
            scrollbar-width: thin;
            scrollbar-color: transparent transparent;
        }
        .dropdown-item {
            padding: 10px;
            cursor: pointer;
            white-space: nowrap;
            overflow-x: hidden;
        }
        .dropdown-item:hover, .dropdown-item.selected {
            background-color: #b4d7e0;
        }
        a {
            text-decoration: none;
            color: inherit;
        }
        a:visited {
            color: inherit;
        }
        .tagcloud span {
            transition: opacity 1s ease, font-size 1s ease, transform 0.5s ease;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: flex-start;
        }
        .bold {
            font-weight: bold;
        }
        .large {
            font-size: 3.5vh;
        }
        #qr-code {
            height: 7em;
            width: 7em;
            display: none;
        }
        #image-display {
            display: none;
            width: 0px;
            height: 0px;
        }
        @media (max-width: 768px) {
            .content-container {
                flex-direction: column;
                padding-bottom: 0;
            }
            .tagcloud, .description {
                width: 100%;
                height: auto;
            }
            .description-bottom {
                height: auto;
            }
            .footer {
                height: auto;
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
</head>
<body>
    <div class="edition-banner">Версія {{ edition_date }}</div>
    <div class="pdf-download">Зберегти як PDF-файл</div>
    <div class="content-container">
        <div class="tagcloud"></div>
        <div class="description">
            <pre class="description-top" id="tag-description-top">Скористайтеся хмарою можливостей <b><a href="https://chat.whatsapp.com/Ip2RBXXucyUFvNB1ysAzMZ">команди грантової підтримки</a></b><br><br>Просто натисніть на те, що Вас зацікавило зліва<br><br>Або введіть свій запит у полі нижче, якщо знаєте, що шукаєте<br><br><br><br><b><u>Важлива примітка</u>:<br><i>майже все тут клікабельне (QR-коди в тому числі) 😉</i></b></pre>
            <div class="description-bottom" id="tag-description-bottom"></div>
        </div>
    </div>
    <div class="footer">
        <div id="dropdown" class="dropdown"></div>
        <input type="text" id="search-input" placeholder="Мені потрібна ця конкретна можливість...">
        <a id="qr-link" href="" target="_blank">
            <img id="qr-code" src="" alt="QR Code">
        </a>
    </div>
    <img id="image-display" src="" style="display:none;"/>
    <script src="https://cdn.jsdelivr.net/npm/TagCloud@2.2.0/dist/TagCloud.min.js"></script>
    <script>
        const myTags = {{ my_tags | tojson }};
        const tagDescriptions = {{ tag_descriptions | tojson }};
        const tagBottomDescriptions = {{ tag_bottom_descriptions | tojson }};  // New variable for column 5
        const qrCodes = {{ qr_codes | tojson }};
        const urls = {{ urls | tojson }};
        const images = {{ images | tojson }};
        const colors = ['#b80000', '#214d96', '#000000'];
        let tagCloud = TagCloud('.tagcloud', myTags, {
            radius: 300,
            maxSpeed: 'fast',
            initSpeed: 'fast',
            direction: 135,
            keep: true
        });
        let isPaused = false;
        let currentClickedTag = null;
        let originalPositions = {};
        let originalDescription = "Скористайтеся хмарою можливостей <b><a href='https://chat.whatsapp.com/Ip2RBXXucyUFvNB1ysAzMZ'>команди грантової підтримки</a></b><br><br>Просто натисніть на те, що Вас зацікавило зліва<br><br>Або введіть свій запит у полі нижче, якщо знаєте, що шукаєте<br><br><br><br><b><u>Важлива примітка</u>:<br><i>майже все тут клікабельне (QR-коди в тому числі) 😉</i></b>";
        let selectedDropdownIndex = -1; 
        function showImage(tag) {
            const imgElement = document.getElementById('image-display');
            imgElement.src = images[tag.textContent];
            imgElement.style.display = 'block';
            const cloudCenter = document.querySelector('.tagcloud').getBoundingClientRect();
            const centerX = cloudCenter.left + 10; 
            const centerY = cloudCenter.top + cloudCenter.height * 0.6; 
            imgElement.style.left = `${centerX}px`;
            imgElement.style.top = `${centerY}px`; 
            imgElement.style.position = 'absolute';
            imgElement.style.zIndex = '10';
        }
        function hideImage() {
            const imgElement = document.getElementById('image-display');
            imgElement.style.display = 'none';
        }
        function toggleTagCloudRotation(tag) {
            if (isPaused) {
                tagCloud.resume(); 
                resetTagsOpacity();
                removeBoldStyle();
                removeLargeStyle();
                resetTagPosition();
                hideImage();  
                document.getElementById('tag-description-top').innerHTML = originalDescription;
                document.getElementById('qr-code').style.display = 'none';
                document.getElementById('tag-description-bottom').style.display = 'none'; // Hide description-bottom
            } else {
                tagCloud.pause(); 
                hideOtherTags(tag);
                addBoldStyle(tag);
                addLargeStyle(tag);
                moveTagToLeft(tag);
                const qrCode = qrCodes[tag.textContent];
                const url = urls[tag.textContent];
                document.getElementById('qr-code').src = qrCode; 
                document.getElementById('qr-code').style.display = 'block'; 
                document.getElementById('qr-link').href = url;
                showImage(tag);
                setTagWidth(tag);
                document.getElementById('tag-description-bottom').style.display = 'block'; // Show description-bottom
                document.getElementById('tag-description-bottom').innerHTML = tagBottomDescriptions[tag.textContent];  // Set column 5 data
            }
            isPaused = !isPaused;
            currentClickedTag = isPaused ? tag : null;
        }
        function hideOtherTags(selectedTag) {
            document.querySelectorAll('.tagcloud span').forEach(tag => {
                if (tag !== selectedTag) {
                    tag.style.opacity = '0';
                }
            });
            const description = tagDescriptions[selectedTag.textContent];
            document.getElementById('tag-description-top').innerHTML = description;
        }
        function resetTagsOpacity() {
            document.querySelectorAll('.tagcloud span').forEach(tag => {
                tag.style.opacity = '1';
            });
        }
        function addBoldStyle(tag) {
            tag.classList.add('bold');
        }
        function removeBoldStyle() {
            document.querySelectorAll('.tagcloud span').forEach(tag => {
                tag.classList.remove('bold');
            });
        }
        function addLargeStyle(tag) {
            tag.classList.add('large');
            tag.style.display = 'flex';
            tag.style.alignItems = 'center';
            const imgElement = tag.querySelector('img');
            if (imgElement) {
                imgElement.style.width = '200px'; 
                imgElement.style.height = 'auto'; 
            }
        }
        function removeLargeStyle() {
            document.querySelectorAll('.tagcloud span').forEach(tag => {
                tag.classList.remove('large');
                tag.style.display = 'inline';  // Reset display
                const imgElement = tag.querySelector('img');
                if (imgElement) {
                    imgElement.style.width = '0px'; 
                    imgElement.style.height = '0px'; 
                }
            });
        }
        function moveTagToLeft(tag) {
            tag.style.transform = 'translate(-50%, -50%) scale(1.5)'; 
        }
        function resetTagPosition() {
            document.querySelectorAll('.tagcloud span').forEach(tag => {
                tag.style.transform = originalPositions[tag.textContent];
            });
        }
        function setTagWidth(tag) {
            const tagCloudWidth = document.querySelector('.tagcloud').offsetWidth;
            tag.style.width = `${tagCloudWidth * 0.65}px`;
        }
        setInitialColor();
        setInterval(updateTagColors, 5000); 
        function setInitialColor() {
            document.querySelectorAll('.tagcloud span').forEach((tag, index) => {
                tag.style.color = colors[index % colors.length];
                originalPositions[tag.textContent] = tag.style.transform; 
                const imgElement = document.createElement('img');
                imgElement.src = images[tag.textContent];
                imgElement.style.width = '0px'; 
                imgElement.style.height = '0px';
                imgElement.style.marginRight = '5px';
                tag.insertBefore(imgElement, tag.firstChild); 
            });
        }
        function updateTagColors() {
            document.querySelectorAll('.tagcloud span').forEach((tag, index) => {
                if (!tag.classList.contains('bold')) {
                    tag.style.color = colors[Math.floor(Math.random() * colors.length)];
                }
            });
        }
        const searchInput = document.getElementById('search-input');
        const dropdown = document.getElementById('dropdown');
        let isMouseHovering = false; 
        searchInput.addEventListener('input', function(event) {
            const inputValue = this.value.toLowerCase();
            dropdown.innerHTML = '';
            selectedDropdownIndex = -1; // Reset index
            const lastChar = event.data; // Get the last character input
            if (lastChar && /^[a-zA-Z0-9!?.]/.test(lastChar)) { 
                const matchingTags = myTags.filter(tag => tag.toLowerCase().includes(inputValue));
                if (matchingTags.length === 1) {
                    const matchedTag = matchingTags[0];
                    if (searchInput.value !== matchedTag) {
                        searchInput.value = matchedTag; 
                        selectTag(matchedTag); // Automatically select if it's the only match
                    }
                    dropdown.style.display = 'none';
                } else if (matchingTags.length > 1) {
                    matchingTags.forEach(tag => {
                        const item = document.createElement('div');
                        item.classList.add('dropdown-item');
                        item.textContent = tag;
                        item.addEventListener('mouseenter', () => {
                            resetDropdownSelection();
                            item.classList.add('selected');
                            isMouseHovering = true; 
                            selectedDropdownIndex = -1; 
                        });
                        item.addEventListener('mouseleave', () => {
                            item.classList.remove('selected');
                        });
                        item.addEventListener('click', () => {
                            selectTag(tag);
                        });
                        dropdown.appendChild(item);
                    });
                    dropdown.style.display = 'block';
                    document.querySelector('.tagcloud').style.opacity = '0'; 
                } else {
                    dropdown.style.display = 'none';
                }
            } else {
                dropdown.style.display = 'none';
                document.querySelector('.tagcloud').style.opacity = '1';
            }
        });
        searchInput.addEventListener('input', function() {
            if (this.value === '') {
                if (isPaused) { 
                    toggleTagCloudRotation(currentClickedTag);
                }
            }
        });
        searchInput.addEventListener('keydown', (event) => {
            if (['Backspace', 'Delete'].includes(event.key)) {
                dropdown.style.display = 'none';
            }
        });
        searchInput.addEventListener('focus', () => {
            dropdown.style.display = ''; 
        });
        searchInput.addEventListener('keydown', (event) => {
            const items = dropdown.querySelectorAll('.dropdown-item');
            if (isMouseHovering) {
                return;
            }
            if (event.key === 'ArrowDown') {
                selectedDropdownIndex = Math.min(selectedDropdownIndex + 1, items.length - 1);
                resetDropdownSelection(); // Clear previous selections
                items[selectedDropdownIndex].classList.add('selected');
                event.preventDefault();
            } else if (event.key === 'ArrowUp') {
                selectedDropdownIndex = Math.max(selectedDropdownIndex - 1, 0);
                resetDropdownSelection(); // Clear previous selections
                items[selectedDropdownIndex].classList.add('selected');
                event.preventDefault();
            } else if (event.key === 'Enter') {
                if (selectedDropdownIndex >= 0) {
                    selectTag(items[selectedDropdownIndex].textContent);
                }
            }
        });
        function resetDropdownSelection() {
            const items = dropdown.querySelectorAll('.dropdown-item');
            items.forEach(item => {
                item.classList.remove('selected');
            });
        }
        searchInput.addEventListener('blur', () => {
            isMouseHovering = false; // Reset when the input loses focus
        });
        searchInput.addEventListener('focus', () => {
            if (dropdown.innerHTML) {
                dropdown.style.display = 'block';
            }
        });
        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                dropdown.style.display = 'none';
                document.querySelector('.tagcloud').style.opacity = '1'; // Reset tag cloud opacity
            }, 200);
        });
        searchInput.addEventListener('keydown', (event) => {
            const items = dropdown.querySelectorAll('.dropdown-item');
            if (event.key === 'ArrowDown') {
                selectedDropdownIndex = Math.min(selectedDropdownIndex + 1, items.length - 1);
                updateDropdownSelection(items);
                event.preventDefault(); 
            } else if (event.key === 'ArrowUp') {
                selectedDropdownIndex = Math.max(selectedDropdownIndex - 1, 0);
                updateDropdownSelection(items);
                event.preventDefault(); 
            } else if (event.key === 'Enter') {
                if (selectedDropdownIndex >= 0) {
                    selectTag(items[selectedDropdownIndex].textContent);
                }
            }
        });
        function updateDropdownSelection(items) {
            items.forEach((item, index) => {
                item.classList.toggle('selected', index === selectedDropdownIndex);
            });
            if (selectedDropdownIndex >= 0) {
                const selectedItem = items[selectedDropdownIndex];
                const dropdownHeight = dropdown.offsetHeight;
                const selectedItemHeight = selectedItem.offsetHeight;
                const selectedItemTop = selectedItem.offsetTop;
                if (selectedItemTop < dropdown.scrollTop) {
                    dropdown.scrollTop = selectedItemTop; 
                } else if (selectedItemTop + selectedItemHeight > dropdown.scrollTop + dropdownHeight) {
                    dropdown.scrollTop = selectedItemTop + selectedItemHeight - dropdownHeight; 
                }
            }
        }
        function selectTag(tag) {
            searchInput.value = tag;
            dropdown.innerHTML = '';
            dropdown.style.display = 'none';
            const selectedTagElement = [...document.querySelectorAll('.tagcloud span')].find(t => t.textContent === tag);
            if (selectedTagElement) {
                toggleTagCloudRotation(selectedTagElement);
            }
            document.querySelector('.tagcloud').style.opacity = '1'; // Reset tag cloud opacity
        }
        document.querySelectorAll('.tagcloud span').forEach(tag => {
            tag.addEventListener('click', (event) => {
                const clickedTag = event.currentTarget;
                if (currentClickedTag === clickedTag) {
                    toggleTagCloudRotation(null);
                } else {
                    toggleTagCloudRotation(clickedTag);
                }
            });
        });
    </script>
</body>
</html>
    """
    rendered_html = Template(template_string).render(
        my_tags=my_tags,
        tag_descriptions=tag_descriptions,
        tag_bottom_descriptions=tag_bottom_descriptions,  # Pass column 5 data to the template
        qr_codes=qr_codes,
        urls=urls,
        images=images,
        edition_date=edition_date
    )
    output_html_path = os.path.join(output_dir, 'index.html')
    with open(output_html_path, 'w', encoding='utf-8') as htmlfile:
        htmlfile.write(rendered_html)

def generate_qr_code(data, output_dir):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="lightgrey")
    qr_code_filename = f"qr_{hashlib.md5(data.encode()).hexdigest()}.png"
    qr_code_path = os.path.join(output_dir, qr_code_filename)
    img.save(qr_code_path)
    return qr_code_filename

def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(base_dir, 'files')
    os.makedirs(files_dir, exist_ok=True)
    spreadsheet_id = '1KUm0d2ieWXLM9iwAGIiIOs2ePDCnApBe88GuRbf3Qr8'  
    try:
        csv_filepath = get_google_sheet(spreadsheet_id, files_dir)
        generate_html_from_csv(csv_filepath, files_dir)
        print("\nГенерація вебсайту завершена. Завантажте його на Github\n\nДля цього зробіть наступні речі:\n1.Відкрийте github.com/login та зайдіть на акаунт nd4s\n2.Відкрийте іконку справа згори та тисніть:\n- Your repositories => gs\n- Add files => Upload files\n3.Відкрийте згенеровану папку files, а у ній файл index.html \n(аби перевірити, що все працює, як треба)\n4.Якщо все вірно, то перетягніть файли з папки у Github\n5.Готово! Натисніть Commit changes та очікуйте до 5 хвилин\n\nУ разі виникнення помилок повторіть процес або зверніться до адміністратора")
    except Exception as e:
        print(f"\nТрапилася наступна помилка. Зверніться з цим текстом до адміністратора: {str(e)}")