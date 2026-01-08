import asyncio
import os
from playwright.async_api import async_playwright

async def show_bus_load_page():
    """
    EaseMyTrip Bus Load Page - Python with Playwright
    यह script bus booking load page को browser में display करता है
    """
    
    # HTML content for bus load page
    html_content = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EaseMyTrip - Bus Booking Loading</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }

        .loading-container {
            text-align: center;
            background: white;
            padding: 60px 80px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .logo {
            width: 200px;
            margin-bottom: 30px;
        }

        .bus-animation {
            position: relative;
            width: 300px;
            height: 150px;
            margin: 0 auto 40px;
        }

        .bus {
            width: 120px;
            height: 80px;
            background: linear-gradient(to bottom, #e74c3c 0%, #c0392b 100%);
            border-radius: 10px 10px 5px 5px;
            position: absolute;
            left: 0;
            top: 30px;
            animation: moveBus 3s ease-in-out infinite;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .bus::before {
            content: '';
            position: absolute;
            width: 100%;
            height: 20px;
            background: #3498db;
            top: -20px;
            border-radius: 10px 10px 0 0;
        }

        .bus::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 8px;
            background: #f39c12;
            bottom: -8px;
            border-radius: 0 0 5px 5px;
        }

        .window {
            width: 25px;
            height: 20px;
            background: rgba(255, 255, 255, 0.8);
            position: absolute;
            top: -15px;
            border-radius: 3px;
        }

        .window1 { left: 10px; }
        .window2 { left: 40px; }
        .window3 { left: 70px; }

        .wheel {
            width: 25px;
            height: 25px;
            background: #2c3e50;
            border-radius: 50%;
            position: absolute;
            bottom: -12px;
            animation: rotate 1s linear infinite;
            border: 3px solid #34495e;
        }

        .wheel1 { left: 15px; }
        .wheel2 { right: 15px; }

        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        @keyframes moveBus {
            0%, 100% {
                left: 0;
            }
            50% {
                left: calc(100% - 120px);
            }
        }

        .road {
            width: 100%;
            height: 4px;
            background: repeating-linear-gradient(
                to right,
                #34495e 0px,
                #34495e 20px,
                transparent 20px,
                transparent 40px
            );
            position: absolute;
            bottom: 30px;
            animation: moveRoad 1s linear infinite;
        }

        @keyframes moveRoad {
            from { background-position: 0 0; }
            to { background-position: 40px 0; }
        }

        h2 {
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 20px;
            font-weight: 600;
        }

        .loading-text {
            color: #7f8c8d;
            font-size: 16px;
            margin-bottom: 30px;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(to right, #667eea, #764ba2);
            border-radius: 10px;
            animation: fillProgress 3s ease-in-out infinite;
        }

        @keyframes fillProgress {
            0% { width: 0%; }
            50% { width: 100%; }
            100% { width: 0%; }
        }

        .status-messages {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 20px;
        }

        .status-item {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            color: #7f8c8d;
            font-size: 14px;
            opacity: 0;
            animation: fadeInStatus 0.5s ease forwards;
        }

        .status-item:nth-child(1) { animation-delay: 0.5s; }
        .status-item:nth-child(2) { animation-delay: 1s; }
        .status-item:nth-child(3) { animation-delay: 1.5s; }
        .status-item:nth-child(4) { animation-delay: 2s; }

        @keyframes fadeInStatus {
            to {
                opacity: 1;
            }
        }

        .checkmark {
            width: 16px;
            height: 16px;
            border: 2px solid #27ae60;
            border-radius: 50%;
            position: relative;
        }

        .checkmark::after {
            content: '✓';
            position: absolute;
            color: #27ae60;
            font-size: 12px;
            top: -2px;
            left: 2px;
        }

        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid #ecf0f1;
            border-top-color: #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .dots {
            display: inline-block;
        }

        .dots::after {
            content: '';
            animation: dots 1.5s steps(4, end) infinite;
        }

        @keyframes dots {
            0%, 20% { content: ''; }
            40% { content: '.'; }
            60% { content: '..'; }
            80%, 100% { content: '...'; }
        }

        .bg-element {
            position: absolute;
            opacity: 0.1;
            animation: float 6s ease-in-out infinite;
        }

        .bg-element:nth-child(1) {
            width: 80px;
            height: 80px;
            background: white;
            border-radius: 50%;
            top: 10%;
            left: 10%;
            animation-delay: 0s;
        }

        .bg-element:nth-child(2) {
            width: 60px;
            height: 60px;
            background: white;
            border-radius: 50%;
            top: 70%;
            right: 15%;
            animation-delay: 2s;
        }

        .bg-element:nth-child(3) {
            width: 40px;
            height: 40px;
            background: white;
            border-radius: 50%;
            bottom: 20%;
            left: 20%;
            animation-delay: 4s;
        }

        @keyframes float {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-20px);
            }
        }
    </style>
</head>
<body>
    <div class="bg-element"></div>
    <div class="bg-element"></div>
    <div class="bg-element"></div>

    <div class="loading-container">
        <div class="logo">
            <svg viewBox="0 0 200 50" xmlns="http://www.w3.org/2000/svg">
                <text x="10" y="35" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#667eea">
                    EaseMyTrip
                </text>
            </svg>
        </div>

        <div class="bus-animation">
            <div class="bus">
                <div class="window window1"></div>
                <div class="window window2"></div>
                <div class="window window3"></div>
                <div class="wheel wheel1"></div>
                <div class="wheel wheel2"></div>
            </div>
            <div class="road"></div>
        </div>

        <h2>बस खोजी जा रही है<span class="dots"></span></h2>
        <p class="loading-text">कृपया प्रतीक्षा करें, हम आपके लिए सर्वोत्तम बस विकल्प खोज रहे हैं</p>

        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>

        <div class="status-messages">
            <div class="status-item">
                <div class="checkmark"></div>
                <span>उपलब्ध बसों की खोज हो रही है</span>
            </div>
            <div class="status-item">
                <div class="checkmark"></div>
                <span>किराया और सीटें चेक की जा रही हैं</span>
            </div>
            <div class="status-item">
                <div class="checkmark"></div>
                <span>सर्वोत्तम ऑफर लोड हो रहे हैं</span>
            </div>
            <div class="status-item">
                <div class="spinner"></div>
                <span>परिणाम तैयार किए जा रहे हैं</span>
            </div>
        </div>
    </div>

    <script>
        setTimeout(() => {
            document.querySelector('.loading-text').textContent = 'बस मिल गईं! रीडायरेक्ट हो रहा है...';
        }, 5000);

        const statusItems = document.querySelectorAll('.status-item');
        let currentStatus = 0;

        setInterval(() => {
            if (currentStatus < statusItems.length) {
                const spinner = statusItems[currentStatus].querySelector('.spinner');
                if (spinner) {
                    spinner.className = 'checkmark';
                }
                currentStatus++;
            }
        }, 1200);
    </script>
</body>
</html>
    """
    
    # Create temp HTML file
    html_file = "temp_bus_load.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("🚌 EaseMyTrip Bus Load Page शुरू हो रहा है...")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Load the HTML file
        await page.goto(f'file:///{os.path.abspath(html_file)}')
        
        print("✅ Load page browser में खुल गया है!")
        print("\nStatus Updates:")
        
        # Simulate loading steps with console output
        await asyncio.sleep(1)
        print("  ✓ उपलब्ध बसों की खोज हो रही है...")
        
        await asyncio.sleep(1.5)
        print("  ✓ किराया और सीटें चेक की जा रही हैं...")
        
        await asyncio.sleep(1.5)
        print("  ✓ सर्वोत्तम ऑफर लोड हो रहे हैं...")
        
        await asyncio.sleep(1.5)
        print("  ⏳ परिणाम तैयार किए जा रहे हैं...")
        
        await asyncio.sleep(2)
        print("\n🎉 बस मिल गईं! Loading complete!")
        
        # Take screenshot
        screenshot_dir = "screenshots_playwright"
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        screenshot_path = os.path.join(screenshot_dir, "bus_load_page.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n📸 Screenshot saved: {screenshot_path}")
        
        # Wait for user to see the page
        print("\n⏳ Browser 10 seconds में automatically बंद हो जाएगा...")
        print("या Ctrl+C press करें browser बंद करने के लिए")
        
        await asyncio.sleep(10)
        
        await browser.close()
        
        # Clean up temp file
        if os.path.exists(html_file):
            os.remove(html_file)
        
        print("\n✅ Program complete!")

if __name__ == "__main__":
    try:
        asyncio.run(show_bus_load_page())
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
