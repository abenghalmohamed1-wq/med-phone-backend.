const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'Product.html');
const content = fs.readFileSync(filePath, 'utf-8');

const headBoundary = '</style>\r\n</head>\r\n\r\n<body>';
const scriptBoundary = '    <script>\r\n        const DB_URL';

let [topPart, rest] = content.split('</style>\r\n</head>');
// Try alternative newline formats if strict split fails
if (!rest) {
    [topPart, rest] = content.split('</style>\n</head>');
}

if (!rest) {
    console.log("Could not split on head");
    process.exit(1);
}

const scriptParts = content.split('<script>');
if (scriptParts.length < 2) {
    console.log("Could not find script tag");
    process.exit(1);
}
const bottomPart = '<script>' + scriptParts.slice(1).join('<script>');

const correctBodyHTML = `
<body>
    <header>
        <a href="Home.html" class="logo-section">
            <div class="logo-icon"><i class="fas fa-mobile-alt"></i></div>
            <div class="logo">Med <span>Phone</span></div>
        </a>
        <nav>
            <a href="Home.html">Home</a>
            <a href="Home.html#products">Shop</a>
            <a href="About.html">About</a>
            <a href="Contact.html">Contact</a>
        </nav>
        <div class="header-actions">
            <div class="cart-icon" id="cartIconBtn"><i class="fas fa-shopping-cart"></i> Cart (0)</div>
        </div>
    </header>

    <div class="breadcrumb">
        <a href="Home.html">Home</a>
        <i class="fas fa-chevron-right"></i>
        <a href="Home.html#products">Shop</a>
        <i class="fas fa-chevron-right"></i>
        <span id="breadcrumbName">Product</span>
    </div>

    <main>
        <div class="product-layout">
            <div class="product-gallery">
                <div class="main-image" id="mainImage">
                    <span id="mainEmoji">📱</span>
                    <div class="product-badge-img" id="productBadge" style="display:none;"></div>
                </div>
                <div class="thumbnail-row" id="thumbnailRow"></div>
            </div>
            <div class="product-info">
                <div class="product-cat-tag" id="productCat">Smartphone</div>
                <h1 class="product-name" id="productName">Loading...</h1>
                <div class="rating-row">
                    <span class="stars" id="productStars">★★★★★</span>
                    <span class="rating-count" id="productReviews">(0 reviews)</span>
                </div>
                <div class="price-block">
                    <div>
                        <div class="price-label">Price</div>
                        <div class="price-main" id="productPrice">MAD 0</div>
                        <div id="productOriginalPrice" style="color:rgba(255,255,255,0.7);font-size:16px;text-decoration:line-through;margin-top:6px;display:none;font-weight:600;"></div>
                    </div>
                    <div class="in-stock"><i class="fas fa-check-circle"></i> In Stock</div>
                </div>
                <div id="productDescription" style="font-size:15px;color:var(--text-mid);line-height:1.7;margin-bottom:24px;display:none;padding:16px;background:var(--off-white);border-radius:16px;border:1px solid rgba(0,0,0,0.04);"></div>
                <hr class="section-divider">
                <div id="colorSection">
                    <div class="option-label">Color: <span id="selectedColorName">—</span></div>
                    <div class="color-options" id="colorOptions"></div>
                </div>
                <div id="storageSection" style="display:none;">
                    <hr class="section-divider">
                    <div class="option-label">Storage: <span id="selectedStorage">—</span></div>
                    <div class="storage-options" id="storageOptions"></div>
                </div>
                <div id="ramSection" style="display:none;">
                    <hr class="section-divider">
                    <div class="option-label">RAM: <span id="selectedRam">—</span></div>
                    <div class="storage-options" id="ramOptions"></div>
                </div>
                <hr class="section-divider">
                <div class="specs-grid" id="specsGrid"></div>
                <div class="action-buttons">
                    <button class="btn-cart" onclick="addToCart()"><i class="fas fa-shopping-cart"></i> Add to Cart</button>
                    <button class="btn-buy" onclick="buyNow()"><i class="fas fa-bolt"></i> Buy Now</button>
                    <button class="btn-wishlist" id="wishlistBtn" onclick="toggleWishlist()"><i class="fas fa-heart"></i></button>
                </div>
                <div class="delivery-info">
                    <div class="delivery-row"><i class="fas fa-shipping-fast"></i>
                        <div><strong>Fast Delivery</strong> <span>— 30 MAD · 2-4 business days</span></div>
                    </div>
                    <div class="delivery-row"><i class="fas fa-shield-alt"></i>
                        <div><strong>2-Year Warranty</strong> <span>— Full manufacturer guarantee</span></div>
                    </div>
                    <div class="delivery-row"><i class="fas fa-undo-alt"></i>
                        <div><strong>30-Day Returns</strong> <span>— Free hassle-free returns</span></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="related-section">
            <h2>You Might Also Like</h2>
            <div class="related-grid" id="relatedGrid"></div>
        </div>
    </main>

    <footer>
        <div class="footer-grid">
            <div class="footer-brand">
                <span class="logo">Med <span>Phone</span></span>
                <p>Your trusted destination for premium electronics — smartphones, AirPods, and smartwatches.</p>
                <div class="social-links">
                    <a href="#"><i class="fab fa-facebook"></i></a>
                    <a href="https://www.instagram.com/abenghal__prv" target="_blank"><i class="fab fa-instagram"></i></a>
                    <a href="#"><i class="fab fa-twitter"></i></a>
                    <a href="https://www.linkedin.com/in/mohamed-abenghal-9a0b8430b" target="_blank"><i class="fab fa-linkedin"></i></a>
                </div>
            </div>
            <div class="footer-col">
                <h4>Quick Links</h4>
                <a href="Home.html">Home</a>
                <a href="Home.html#products">Shop</a>
                <a href="About.html">About Us</a>
                <a href="Contact.html">Contact</a>
            </div>
            <div class="footer-col">
                <h4>Categories</h4>
                <a href="Home.html#products">Smartphones</a>
                <a href="Home.html#products">AirPods</a>
                <a href="Home.html#products">Smartwatches</a>
            </div>
        </div>
        <div class="footer-bottom">© 2025 Med Phone — All Rights Reserved</div>
    </footer>

    <div class="add-toast" id="addToast">✓ Added to cart!</div>
    <div class="chat-toggle-btn" id="chatToggle"><i class="fas fa-comments"></i></div>
    <div class="chat-container" id="chatContainer">
        <div class="chat-header">
            <h3><i class="fas fa-mobile-alt"></i> Med Phone Assistant</h3>
            <button class="close-chat" id="closeChat"><i class="fas fa-times"></i></button>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">Hello! Type "specs", "colors", or "price" to learn more about this product!</div>
        </div>
        <div class="chat-input-area">
            <input type="text" class="chat-input" id="chatInput" placeholder="Ask about specs, shipping...">
            <button class="send-btn" id="sendMessage"><i class="fas fa-paper-plane"></i></button>
        </div>
    </div>

    `;

const finalHTML = topPart + '</style>\n</head>\n' + correctBodyHTML + bottomPart;
fs.writeFileSync(filePath, finalHTML);
console.log("SUCCESS");
