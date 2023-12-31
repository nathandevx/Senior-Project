from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files import File
from faker import Faker
from home.models import Product, ProductImage, ShippingAddress, Cart, CartItem, Order
from blog.models import Post
from datetime import datetime, date
import warnings


warnings.filterwarnings("ignore")

faker = Faker()
User = get_user_model()
superuser = User.objects.filter(is_superuser=True).first()

admins = User.objects.filter(groups__name='ADMIN', is_superuser=False)
ADMIN1 = admins[0]
ADMIN2 = admins[1]
ADMIN3 = admins[2]
ADMIN4 = admins[3]
ADMIN5 = admins[4]

customers = User.objects.filter(groups__name='CUSTOMER', is_superuser=False)
CUSTOMER1 = customers[0]
CUSTOMER2 = customers[1]
CUSTOMER3 = customers[2]
CUSTOMER4 = customers[3]
CUSTOMER5 = customers[4]

# Dummy product data
PRODUCT = {
	"name": ["Muffin", "Fudge", "Baklava", "Croissant", "Turnover", "Pretzel", "Donut", "Cookie", "Cupcake", "Brownie", "Bagel", "Cheesecake"],
	"description": [
		"A muffin is a versatile baked snack, typically a single-serving quick bread, that comes in a wide range of flavors and varieties. Muffins are appreciated for their soft and tender crumb, making them a popular choice for breakfast or a convenient on-the-go snack.",
		"Fudge is a rich, indulgent dessert treat made from a blend of chocolate, sugar, and butter, resulting in a dense, smooth texture. It's often enhanced with various flavorings and mix-ins, such as nuts or marshmallows, and enjoyed as a sweet delight.",
		"Baklava is a sweet dessert pastry made from layers of thin, flaky phyllo dough filled with chopped nuts and sweetened with syrup or honey. It's often garnished with ground pistachios or walnuts and is a popular treat in Middle Eastern and Mediterranean cuisine.",
		"Croissants are flaky, buttery pastries with a crescent shape. They are made from layered dough and are known for their light, airy texture and delicious, buttery flavor.",
		"A turnover is a pastry made by folding dough over a sweet or savory filling, typically fruit, jam, or meat. They are often baked to a golden brown and may be drizzled with icing or powdered sugar.",
		"Pretzels are twisted, salty bread snacks, often served warm, with a crisp exterior and a soft interior. They come in various shapes and sizes and are a popular savory snack.",
		"Donuts are deep-fried or baked dough rings or spheres, often coated in glaze or sprinkled with toppings like powdered sugar or cinnamon. They can be filled with various sweet fillings, making them a beloved breakfast or snack item.",
		"Cookies are small, sweet baked goods made from dough, typically containing ingredients like flour, sugar, and butter. They come in countless flavors and shapes, from classic chocolate chip to delicate shortbread.",
		"Cupcakes are individual-sized cakes baked in cup-shaped containers. They come in various flavors and can be topped with frosting, sprinkles, or other decorations, making them a popular choice for celebrations.",
		"Brownies are dense, chocolate-flavored square or rectangular baked treats that strike a balance between cake and cookie. They are known for their rich, fudgy texture and are often studded with nuts or chocolate chips.",
		"A bagel is a round, chewy bread roll that is boiled before it's baked, giving it a distinct dense and doughy texture. Bagels are often sliced and enjoyed with cream cheese, smoked salmon, or various other toppings.",
		"Cheesecake is a rich and creamy dessert made with a smooth, sweetened cream cheese or ricotta cheese filling on a crust, often made from crushed graham crackers or cookies. It's typically baked and can be topped with various toppings like fruit compote or chocolate."
	],
	"extra_description": [
		"<h1>About Muffin</h1><p>A muffin is a versatile and satisfying baked good known for its soft and tender crumb. Whether enjoyed for breakfast or as a snack, muffins come in a variety of flavors and are a beloved choice for a quick, delicious treat.</p><h2>The History of Muffin</h2><p>The history of muffins can be traced back to early 19th-century England. They were initially a type of yeast bread but evolved into the quick bread muffins we know today. Muffins gained popularity in the United States during the 20th century.</p><h3>Muffin Ingredients</h3><p>Muffins are typically made from basic ingredients like flour, sugar, eggs, and milk, with variations in flavorings and mix-ins. Blueberry, chocolate chip, and banana nut are just a few of the many muffin varieties available.</p><p>Muffins offer a delightful blend of sweetness and warmth. They can be enjoyed plain or customized with toppings like streusel or icing.</p><p>Key Ingredients:</p><ul><li>Flour</li><li>Sugar</li><li>Eggs</li><li>Milk</li><li>Flavorings and mix-ins (e.g., blueberries, chocolate chips)</li></ul>",
		"<h1>About Fudge</h1><p>Fudge is a decadent confection known for its rich and creamy texture. It's made by combining sugar, butter, and milk, resulting in a melt-in-your-mouth treat that's beloved by chocolate enthusiasts.</p><h2>The History of Fudge</h2><p>The history of fudge can be traced back to the late 19th century in the United States. It gained popularity as a homemade candy and is now a classic dessert enjoyed worldwide.</p><h3>Fudge Ingredients</h3><p>Fudge typically includes ingredients like sugar, butter, milk, and chocolate, which are heated and mixed to achieve its smooth consistency. Variations may incorporate nuts or flavorings for added depth of flavor.</p><p>Fudge is a delightful dessert that offers a perfect balance of sweetness and creaminess. It's often cut into bite-sized pieces and makes for a delightful gift or indulgent treat.</p><p>Key Ingredients:</p><ul><li>Sugar</li><li>Butter</li><li>Milk</li><li>Chocolate</li><li>Nuts (optional)</li></ul>",
		"<h1>About Baklava</h1><p>Baklava is a sweet dessert pastry known for its layers of thin, flaky phyllo dough filled with chopped nuts and sweetened with syrup or honey. This indulgent treat is a beloved part of Middle Eastern and Mediterranean cuisine, appreciated for its delightful combination of textures and flavors.</p><h2>The History of Baklava</h2><p>Baklava's origins can be traced back to ancient Assyria, where a similar pastry was enjoyed as a treat by royalty. Over time, it spread through the Middle East and Mediterranean regions, each culture adding its unique touch to the recipe. Today, baklava is a symbol of celebration and hospitality.</p><h3>Baklava Ingredients</h3><p>Baklava is made from a handful of key ingredients, including phyllo dough, nuts (typically almonds, walnuts, or pistachios), butter, sugar, and a sweet syrup made from honey or sugar. The layering of phyllo dough and nuts creates its distinctive texture and taste, while the syrup adds a sweet and sticky finish.</p><p>Baklava is a dessert that delights the senses with its crisp layers, nutty richness, and sweet syrup. It's often garnished with ground pistachios or cinnamon, adding an extra layer of flavor. Here is a list of key ingredients:</p><ul><li>Phyllo dough</li><li>Nuts (e.g., almonds, walnuts, pistachios)</li><li>Butter</li><li>Sugar</li><li>Honey or sugar syrup</li></ul><p>Baklava is a dessert that showcases the artistry of layering and is a wonderful treat for special occasions or as a sweet ending to a delicious meal.</p>",
		"<h1>About Croissant</h1><p>A Croissant is a flaky and buttery pastry known for its crescent shape and delicious taste. Originating in France, croissants have become a symbol of French bakery craftsmanship and are loved for their light and airy texture.</p><h2>The History of Croissant</h2><p>The history of croissants can be traced back to Austria, where a pastry known as a 'kipferl' inspired the creation of the croissant in France. Over time, croissants gained worldwide recognition and became a staple in French bakeries. They are often associated with breakfast and brunch menus.</p><h3>Croissant Ingredients</h3><p>Croissants are made from a simple but precise combination of ingredients, including flour, butter, water, yeast, sugar, and salt. The secret to their flakiness lies in the technique of layering butter within the dough through a process called lamination.</p><p>Croissants can be enjoyed in various ways, from plain to filled with chocolate, almond paste, or ham and cheese. They are a versatile and delightful pastry. Here is a list of key ingredients:</p><ul><li>Flour</li><li>Butter</li><li>Water</li><li>Yeast</li><li>Sugar</li><li>Salt</li></ul><p>Croissants are a favorite choice for breakfast or a mid-day treat, and their distinctive shape and flavor make them a memorable pastry experience.</p>",
		"<h1>About Turnover</h1><p>A Turnover is a delightful pastry made by folding dough over a sweet or savory filling. Known for its flaky exterior and flavorful interior, turnovers are a versatile treat that can be enjoyed as a dessert or a savory snack.</p><h2>The History of Turnover</h2><p>The history of turnovers can be traced back to various cultures, where similar pastries were made using regional ingredients. The concept of folding dough over a filling has been enjoyed for centuries and continues to be a popular choice for quick, handheld meals.</p><h3>Turnover Ingredients</h3><p>Turnovers can be filled with a variety of ingredients, including fruits, jams, meats, or vegetables. The choice of filling determines whether they are sweet or savory. The dough is typically made from flour, butter, and water, resulting in a flaky and buttery crust.</p><p>Turnovers are a versatile pastry that can be customized with various fillings to suit different tastes and preferences.</p>",
		"<h1>About Pretzel</h1><p>A Pretzel is a savory and slightly salty bread snack known for its twisted shape and delightful crunch. Whether enjoyed at a sports event, fair, or as a tasty snack, pretzels are a versatile and satisfying treat that appeals to all ages.</p><h2>The History of Pretzel</h2><p>The history of pretzels dates back to Europe, where they were originally made by monks in the early Middle Ages. The twisted shape of pretzels is said to represent arms crossed in prayer. Over time, pretzels became a symbol of good luck and prosperity.</p><h3>Pretzel Ingredients</h3><p>Pretzels are made from simple ingredients, including flour, water, yeast, sugar, and salt. The dough is twisted into shape and briefly boiled before baking, which gives pretzels their characteristic texture and flavor.</p><p>Pretzels come in various forms, from traditional twists to pretzel bites and pretzel dogs. They are a snack that's hard to resist.</p>",
		"<h1>About Donut</h1><p>A Donut is a beloved pastry known for its sweet and indulgent flavor. Whether enjoyed as a breakfast treat or a delightful snack, donuts have a special place in the hearts of many. Their soft, fluffy texture and delectable glaze make them irresistible.</p><h2>The History of Donut</h2><p>The history of donuts is believed to date back to Dutch settlers in the United States during the 18th century. They were originally called 'olykoeks,' which means 'oily cakes.' Donuts have come a long way since then, gaining popularity in various forms, from classic glazed to gourmet creations.</p><h3>Donut Ingredients</h3><p>Donuts are typically made from ingredients like flour, sugar, eggs, and milk. They are deep-fried to perfection, resulting in a delightful golden-brown exterior and a tender interior. The glaze, icing, or toppings add a burst of sweetness and flavor.</p><p>Donuts can be enjoyed in various forms, from classic glazed to jelly-filled or even topped with bacon. They are a treat that brings joy to people of all ages.</p>",
		"<h1>About Cookie</h1><p>A Cookie is a delightful baked treat that comes in countless flavors, shapes, and sizes. Known for its sweet and satisfying taste, cookies are a beloved comfort food enjoyed by people of all ages. Whether dunked in milk or savored with a cup of tea, cookies are a timeless classic.</p><h2>The History of Cookie</h2><p>The history of cookies can be traced back to ancient times, with various forms of cookies being made by different cultures throughout history. Cookies as we know them today have evolved from recipes that originated in Persia. They became popular in Europe and later in the United States, where they gained widespread recognition.</p><h3>Cookie Ingredients</h3><p>Cookies are typically made from basic ingredients such as flour, sugar, butter, eggs, and flavorings like vanilla extract. Mix-ins like chocolate chips, nuts, or dried fruits add texture and flavor. The combination of these ingredients results in the delightful treat we all know and love.</p><p>Cookies can be customized with various ingredients and mix-ins to create endless variations. From chewy chocolate chip cookies to delicate shortbread, there's a cookie for every palate.</p>",
		"<h1>About Cupcake</h1><p>A Cupcake is a charming individual-sized cake that's perfect for celebrations and sweet indulgences. Known for its endless variety of flavors and creative decorations, cupcakes are a favorite among dessert lovers of all ages. Whether enjoyed at birthday parties, weddings, or as a sweet treat, cupcakes never go out of style.</p><h2>The History of Cupcake</h2><p>The history of cupcakes can be traced back to the 19th century in the United States. They were initially baked in teacups, which gave them their name. Over time, cupcakes evolved into the miniature delights we know today. They gained widespread popularity in the early 21st century and are now a symbol of sweet indulgence.</p><h3>Cupcake Ingredients</h3><p>Cupcakes are made from basic ingredients like flour, sugar, butter, eggs, and flavorings. They come in a wide range of flavors, from classic vanilla and chocolate to exotic options like red velvet or lemon. Frosting, sprinkles, and decorative toppings add a touch of creativity to each cupcake.</p><p>Cupcakes are a canvas for bakers to express their creativity, and they can be personalized with various designs and flavor combinations. Whether you're a fan of the classic or the adventurous, there's a cupcake for everyone's taste.</p>",
		"<h1>About Brownie</h1><p>A Brownie is a delectable dessert that strikes the perfect balance between cake and cookie. Known for its rich, fudgy texture and deep chocolate flavor, brownies are a beloved treat enjoyed by people of all ages. Whether served warm with a scoop of ice cream or enjoyed as a snack, brownies are a crowd-pleaser.</p><h2>The History of Brownie</h2><p>The history of brownies is believed to trace back to the late 19th century in the United States. They were originally created as a cake-like dessert but evolved into the dense, chocolaty squares we know today. Brownies have become a staple in American baking and a symbol of indulgence.</p><h3>Brownie Ingredients</h3><p>Brownies typically contain ingredients like chocolate, butter, sugar, eggs, and flour. Nuts, such as walnuts or pecans, are often added for a delightful crunch. The combination of these ingredients results in a delightful dessert that's hard to resist.</p><p>Here is a list of key ingredients:</p><ul><li>Chocolate</li><li>Butter</li><li>Sugar</li><li>Eggs</li><li>Flour</li><li>Nuts (optional)</li></ul><p>Brownies can be customized with various additions, such as chocolate chips or caramel swirls, to suit different preferences. They are a favorite choice for celebrations and sweet indulgences.</p>",
		"<h1>About Bagel</h1><p>A Bagel is a versatile and beloved bread product known for its chewy texture and unique shape. It's a staple in many breakfast menus and is enjoyed in various ways. Bagels come in a wide range of flavors and are a popular choice for a quick, satisfying meal.</p><h2>The History of Bagel</h2><p>The bagel's origins can be traced to Jewish communities in Poland in the 17th century. Over time, it has become a symbol of cultural diversity and is now enjoyed by people worldwide. Bagels are often associated with New York City, where they gained widespread popularity in the early 20th century.</p><h3>Bagel Ingredients</h3><p>Bagels are typically made with simple ingredients, including flour, water, yeast, sugar, and salt. They are boiled briefly before baking, which gives them their signature chewy crust and soft interior. Bagels can be customized with toppings like sesame seeds, poppy seeds, or everything seasoning.</p><p>Bagels are a versatile food that can be enjoyed with various spreads, such as cream cheese, butter, or jam. They are also a popular choice for sandwiches, making them a go-to option for a quick and satisfying meal.</p><p>They are boiled briefly before baking, which gives them their signature chewy crust and soft interior. Bagels can be customized with toppings like sesame seeds, poppy seeds, or everything seasoning.</p><p>Bagels are a versatile food that can be enjoyed with various spreads, such as cream cheese, butter, or jam. They are also a popular choice for sandwiches, making them a go-to option for a quick and satisfying meal.</p>",
		"<h1>About Cheesecake</h1><p>Cheesecake is a beloved dessert known for its rich and creamy texture and delightful flavor. It's a timeless classic that has been enjoyed for generations. Whether you prefer the classic New York style or a fruity variation, cheesecake is a dessert that never disappoints.</p><h2>The History of Cheesecake</h2><p>The history of cheesecake dates back to ancient Greece, where it was served at weddings and other special occasions. Over time, it evolved into the dessert we know today, with various regional adaptations. Now, it's a favorite treat worldwide, loved for its indulgent taste and versatility.</p><h3>Cheesecake Ingredients</h3><p>Cheesecake is typically made with ingredients like cream cheese, sugar, eggs, and a graham cracker crust. Additional flavorings such as vanilla extract or fruit compote can be added for variety. The key to its creamy texture lies in the quality of the cream cheese and the baking process.</p><p>Cheesecake is a dessert that appeals to all ages and tastes, making it a perfect addition to any dessert menu or special occasion. Here is a list of key ingredients:</p><ul><li>Cream cheese</li><li>Sugar</li><li>Eggs</li><li>Graham cracker crust</li><li>Flavorings (e.g., vanilla extract)</li></ul><p>The combination of these ingredients creates a delectable dessert that's hard to resist.</p>",
	],
	"price": [60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5],
	"estimated_delivery_date": [
		datetime(2061, 4, 10, 0, 0),
		datetime(2060, 3, 29, 0, 0),
		datetime(2059, 3, 24, 0, 0),
		datetime(2058, 3, 21, 0, 0),
		datetime(2057, 3, 12, 0, 0),
		datetime(2056, 2, 25, 0, 0),
		datetime(2055, 2, 23, 0, 0),
		datetime(2054, 2, 5, 0, 0),
		datetime(2053, 2, 2, 0, 0),
		datetime(2052, 1, 28, 0, 0),
		datetime(2051, 1, 20, 0, 0),
		datetime(2050, 1, 15, 0, 0)
	],
	"status": [Product.INACTIVE, Product.INACTIVE, Product.ACTIVE, Product.ACTIVE, Product.ACTIVE, Product.ACTIVE, Product.ACTIVE, Product.ACTIVE, Product.ACTIVE, Product.ACTIVE, Product.ACTIVE, Product.ACTIVE],
	"stock": [0, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50],
	"creator": [ADMIN2, ADMIN1, ADMIN5, ADMIN5, ADMIN4, ADMIN4, ADMIN3, ADMIN3, ADMIN2, ADMIN1, ADMIN1, ADMIN2],
	"updater": [ADMIN2, ADMIN1, ADMIN5, ADMIN5, ADMIN4, ADMIN4, ADMIN3, ADMIN3, ADMIN2, ADMIN1, ADMIN1, ADMIN2],
}

PRODUCT_IMAGE = {
	"Muffin": [
		"static/images/demo_product_images/muffin/muffin1.jpg",
		"static/images/demo_product_images/muffin/muffin2.jpg",
		"static/images/demo_product_images/muffin/muffin3.jpg"
	],
	"Fudge": [
		"static/images/demo_product_images/fudge/fudge1.jpg",
		"static/images/demo_product_images/fudge/fudge2.jpg",
		"static/images/demo_product_images/fudge/fudge3.jpg"
	],
	"Baklava": [
		"static/images/demo_product_images/baklava/baklava1.jpg",
		"static/images/demo_product_images/baklava/baklava2.jpg",
		"static/images/demo_product_images/baklava/baklava3.jpg"
	],
	"Croissant": [
		"static/images/demo_product_images/croissant/croissant1.jpg",
		"static/images/demo_product_images/croissant/croissant2.jpg",
		"static/images/demo_product_images/croissant/croissant3.jpg"
	],
	"Turnover": [
		"static/images/demo_product_images/turnover/turnover1.jpg",
		"static/images/demo_product_images/turnover/turnover2.jpg",
		"static/images/demo_product_images/turnover/turnover3.jpg"
	],
	"Pretzel": [
		"static/images/demo_product_images/pretzel/pretzel1.jpg",
		"static/images/demo_product_images/pretzel/pretzel2.jpg",
		"static/images/demo_product_images/pretzel/pretzel3.jpg"
	],
	"Donut": [
		"static/images/demo_product_images/donut/donut1.jpg",
		"static/images/demo_product_images/donut/donut2.jpg",
		"static/images/demo_product_images/donut/donut3.jpg"
	],
	"Cookie": [
		"static/images/demo_product_images/cookie/cookie1.jpg",
		"static/images/demo_product_images/cookie/cookie2.jpg",
		"static/images/demo_product_images/cookie/cookie3.jpg"
	],
	"Cupcake": [
		"static/images/demo_product_images/cupcake/cupcake1.jpg",
		"static/images/demo_product_images/cupcake/cupcake2.jpg",
		"static/images/demo_product_images/cupcake/cupcake3.jpg"
	],
	"Brownie": [
		"static/images/demo_product_images/brownie/brownie1.jpg",
		"static/images/demo_product_images/brownie/brownie2.jpg",
		"static/images/demo_product_images/brownie/brownie3.jpg"
	],
	"Bagel": [
		"static/images/demo_product_images/bagel/bagel1.jpg",
		"static/images/demo_product_images/bagel/bagel2.jpg",
		"static/images/demo_product_images/bagel/bagel3.jpg"
	],
	"Cheesecake": [
		"static/images/demo_product_images/cheesecake/cheesecake1.jpg",
		"static/images/demo_product_images/cheesecake/cheesecake2.jpg",
		"static/images/demo_product_images/cheesecake/cheesecake3.jpg"
	],
}

BLOG_POSTS = {
	"title": ["A Blog Post About Cheesecakes", "A Blog Post About Bagels", "A Blog Post About Brownies", "A Blog Post About Cupcakes", "A Blog Post About Cookies", "A Blog Post About Donuts"],
	"preview_text": [
		"Delve into the decadent world of cheesecakes, a dessert that transcends time from ancient Greece to today's dessert tables. Uncover the rich history and diverse styles of this beloved treat, from the dense New York classic to the fluffy Japanese delight.",
		"Explore the world of bagels, where each ring-shaped delight tells a tale of culinary tradition and innovation. This article delves into the bagel's unique texture and versatility, from classic New York-style to inventive contemporary variations.",
		"Dive into the indulgent world of brownies, where every bite is a blend of rich chocolate and delightful textures. This article explores the journey of brownies from a simple chocolate treat to a beloved dessert staple across the globe.",
		"Embark on a delightful journey into the world of cupcakes, where creativity and flavor collide in a small, yet spectacular treat. Discover how these charming mini-cakes have captivated hearts and taste buds alike with their endless varieties and decorative charm.",
		"Step into the delightful world of cookies, a simple yet beloved treat that brings comfort and joy with each bite. This article explores the vast array of cookie varieties and the rich history behind this universally adored baked good.",
		"Journey into the delectable universe of donuts, where each golden ring narrates a story of sweet indulgence and culinary creativity. This article explores the world of donuts, from traditional glazed classics to imaginative and mouthwatering modern variations.",
	],
	"content": [
		"<h1>A blog post about Cheesecakes</h1><p>Cheesecake is more than just a dessert; it's a symbol of culinary delight and creativity. Originating from a simple recipe, today's cheesecakes have evolved into a diverse range of styles and flavors, catering to all tastes and occasions. The beauty of cheesecake lies in its versatility, from the classic New York-style cheesecake, known for its creamy richness and smooth texture, to the light and fluffy Japanese cheesecake that melts in your mouth like a cloud. Each variety offers a unique experience, blending the richness of cream cheese with flavors like strawberry, blueberry, or even exotic passion fruit. Cheesecakes can be baked or set, with various crusts ranging from the traditional graham cracker base to inventive Oreo or nut-based alternatives. The allure of this dessert also lies in its presentation, often garnished with fruit, chocolate, or a glaze that adds an extra layer of flavor and elegance. Whether it's for a celebration, a family gathering, or simply as a treat to oneself, cheesecake remains a beloved choice that satisfies the sweet tooth of connoisseurs and casual dessert lovers alike.</p><h2>The History of Cheesecakes</h2><p>The history of cheesecake is as rich and layered as the dessert itself. Its origins can be traced back to ancient Greece, where it was considered a source of energy and even served to athletes at the first Olympic games. The Roman conquest of Greece saw this delicacy spread across Europe, where it underwent various adaptations. The introduction of cream cheese in the 18th century was a pivotal moment in the evolution of the cheesecake. This key ingredient revolutionized the texture and taste, setting the stage for the modern cheesecake we know today. In the United States, cheesecake truly found its footing, with each region developing its own take on this classic. The New York-style cheesecake, in particular, gained fame for its use of extra eggs and cream, resulting in a dense, smooth, and creamy cake. Over time, the cheesecake has become a canvas for culinary artistry, blending tradition with innovation, and solidifying its status as a global favorite. Every bite of cheesecake is not just a taste of deliciousness, but also a piece of culinary history that spans centuries and continents.</p><ul><li><strong>New York Cheesecake:</strong> Known for its rich, dense texture and smooth, creamy flavor.</li><li><strong>Japanese Cheesecake:</strong> Airy, light, and fluffy, often likened to a cotton-soft texture.</li><li><strong>Italian Ricotta Cheesecake:</strong> Made with ricotta cheese, offering a slightly grainy texture and a delicately sweet flavor.</li></ul>",
		"<h1>A blog post about Bagels</h1><p>Bagels are more than just a breakfast staple; they're a culinary icon with a unique texture and versatility that has captivated palates worldwide. Originating from Jewish communities in Poland, bagels have become a global phenomenon, symbolizing comfort food with their dense, chewy texture and distinctive doughy quality. The classic New York-style bagel, boiled before baking, achieves a shiny, crisp exterior and soft, chewy interior, making it the perfect canvas for a variety of toppings from cream cheese to smoked salmon. Beyond the traditional, bagels have evolved into a canvas for culinary creativity, ranging from sweet varieties dotted with cinnamon raisin to savory selections adorned with everything seasoning. Their versatility extends beyond spreads and toppings; bagels serve as the base for a myriad of sandwiches, offering a satisfying heft and flavor. Whether enjoyed at a bustling city deli or a cozy café, the bagel transcends cultural boundaries, embodying a fusion of tradition and modern gastronomy. Each variety, from the simplest plain bagel to the most elaborate flavored ones, represents a piece of the bagel's rich cultural tapestry.</p><h2>The History of Bagels</h2><p>The bagel's journey from a local Jewish community staple to an international breakfast favorite is a story steeped in tradition and resilience. The bagel's origins trace back to the Jewish communities of Poland in the 17th century, where it was a gift to women in childbirth, symbolizing the cycle of life with its circular shape. The bagel's migration to America, particularly New York, in the late 19th century with Eastern European immigrants, marked a pivotal chapter in its history. In New York, the bagel found its second home, thriving in the city's Jewish bakeries and becoming a quintessential New York food. The introduction of automated bagel-making machines in the mid-20th century propelled bagels into mainstream American cuisine, increasing their popularity and availability. Today, bagels are not just a Jewish or American delicacy but a global phenomenon, enjoyed in various forms and flavors across the world. From their humble beginnings to their current status as a beloved food item, bagels have remained true to their roots while adapting to the tastes of each generation.</p><ul><li><strong>Plain Bagel:</strong> The classic choice, perfect for any topping.</li><li><strong>Everything Bagel:</strong> Topped with a mix of sesame seeds, poppy seeds, onion, garlic, and salt.</li><li><strong>Cinnamon Raisin Bagel:</strong> A sweet twist, ideal for a breakfast treat.</li></ul>",
		"<h1>A blog post about Brownies</h1><p>Brownies are the quintessential sweet treat for chocolate lovers, blending the richness of a cake with the chewy texture of a cookie. Originating in the United States, brownies have become a global phenomenon, beloved for their dense, fudgy texture and deep chocolate flavor. Whether served as a warm dessert with ice cream or enjoyed as a snack, brownies offer a satisfying and indulgent experience. The beauty of brownies lies in their simplicity and adaptability; they can be enhanced with nuts, swirled with caramel, or topped with frosting, each variation adding a unique twist to the classic recipe. Their versatility makes them a favorite at gatherings, bake sales, and as a comforting homemade treat. Brownies can range from cake-like to fudgy or even gooey, depending on the ratio of flour to chocolate and butter. This delightful dessert continues to evolve, with creative bakers experimenting with ingredients like black beans and sweet potatoes, catering to a variety of dietary preferences and palates. Every batch of brownies, whether classic or innovative, promises a moment of chocolatey bliss.</p><h2>The History of Brownies</h2><p>The story of brownies began in the late 19th century in the United States, a product of America's love affair with chocolate. The first brownie recipes were a simple combination of butter, sugar, chocolate, eggs, and flour, creating a dense, cake-like dessert. Over time, brownies evolved to include variations like the addition of nuts or frosting. The exact origin of brownies is shrouded in myth, with some stories suggesting they were created by accident when a baker forgot to add baking powder to a chocolate cake batter. Regardless of their origin, brownies quickly became a staple of American baking, finding their way into home kitchens and cookbooks across the country. The 20th century saw the rise of boxed brownie mixes, making the dessert accessible to even novice bakers. Today, brownies are celebrated for their simplicity and versatility, with countless recipes and variations available, each promising the rich, chocolatey taste that has made them a timeless classic.</p><ul><li><strong>Classic Chocolate Brownie:</strong> Rich and fudgy, often studded with chocolate chips.</li><li><strong>Walnut Brownie:</strong> Crunchy walnuts add texture to the dense chocolate base.</li><li><strong>Blondie:</strong> A vanilla-based twist on the traditional brownie, often filled with chocolate chips or nuts.</li></ul>",
		"<h1>A blog post about Cupcakes</h1><p>Cupcakes, the charming little delights that have become synonymous with celebration and creativity, are more than just miniature cakes. They represent a world of culinary artistry in a bite-sized form, offering endless possibilities in flavors, decorations, and themes. The allure of cupcakes lies in their individuality; each one can be personalized to suit different tastes and occasions. From classic vanilla and rich chocolate to exotic flavors like salted caramel or lavender, there's a cupcake for every palate. The joy of cupcakes also extends to their decoration – with frosting, sprinkles, edible flowers, and intricate designs turning each one into a work of art. These tiny treasures are not just a dessert; they're a canvas for bakers and decorators to express their creativity and delight their audience. Cupcakes have a special way of bringing joy and adding a touch of whimsy to any gathering, be it a birthday party, wedding, or just a casual get-together. Their popularity is not just due to their delicious taste but also their ability to bring people together, making every occasion a little more special and memorable.</p><h2>The History of Cupcakes</h2><p>The history of cupcakes is a journey back to the 19th century when they emerged as a convenient and quicker alternative to traditional cakes. The term 'cupcake' originally referred to the small cups or ramekins in which these cakes were baked, a practice that allowed for faster cooking times than larger cakes. Over the years, cupcakes evolved from simple, plain cakes to elaborate creations that are as much a feast for the eyes as they are for the taste buds. The 21st century, in particular, witnessed a cupcake renaissance, with boutique cupcake shops popping up around the world, and television shows dedicated to cupcake baking and decorating contests. Cupcakes became a trend, a symbol of gourmet baking, and a means to showcase baking innovation and trendiness. From their humble beginnings, cupcakes have risen to fame, becoming a beloved treat for all ages and a staple in modern baking. They have evolved from simple home-baked goods to gourmet creations, marking their place in the culinary world as both a classic and a trendsetter.</p><ul><li><strong>Red Velvet Cupcake:</strong> A classic with its distinctive red color and cream cheese frosting.</li><li><strong>Chocolate Cupcake:</strong> Rich and indulgent, a timeless favorite for chocolate lovers.</li><li><strong>Vegan Cupcake:</strong> A plant-based option that doesn't compromise on flavor or texture.</li></ul>",
		"<h1>A blog post about Cookies</h1><p>Cookies, the universally adored sweet treats, range from the classic chocolate chip to the sophisticated macaron, embodying the essence of comfort food and baking artistry. These small, flat, and sweet baked goods have a special place in cultures worldwide, serving as a symbol of homemade warmth and creative baking. The variety of cookies is astounding, each with its unique texture, flavor, and appearance. From the chewy and soft to the crisp and crumbly, there's a cookie to match every mood and palate. Whether they're enjoyed with a glass of milk as a nostalgic snack, savored with a cup of tea or coffee, or used as a base for more elaborate desserts, cookies are a staple in the world of baking. Their versatility extends to their ingredients, with endless combinations of flour, butter, sugar, chocolate, nuts, and fruits. The art of cookie-making allows for both traditional recipes passed down through generations and innovative creations that push the boundaries of taste and presentation. Cookies are more than just a snack; they represent a universal language of love and comfort, bringing people together and making any moment a bit sweeter.</p><h2>The History of Cookies</h2><p>The history of cookies dates back centuries, with their origins rooted in 7th century Persia, one of the first countries to cultivate sugar. The concept of the cookie began as small test cakes, where bakers used a small amount of batter to test oven temperatures. These evolved into sweet, portable treats that traveled well, making them popular on long journeys during the Middle Ages. Cookies spread throughout Europe, thanks to the Muslim conquest of Spain and the spice trade routes. Each region added its local flavors and ingredients, leading to the diverse range of cookies we know today. The cookie made its way to the Americas with European settlers, where it was embraced and reinvented in countless forms. Today, cookies are a global phenomenon, an integral part of culinary traditions and modern snacking culture. They have been adapted to suit local tastes and ingredients, resulting in a rich tapestry of flavors and forms that continue to evolve and delight.</p><ul><li><strong>Chocolate Chip Cookie:</strong> The classic favorite, packed with gooey chocolate chips.</li><li><strong>Oatmeal Raisin Cookie:</strong> A chewy, wholesome option with sweet raisins and spices.</li><li><strong>Shortbread Cookie:</strong> A buttery and crumbly delight, perfect for tea time.</li></ul>",
		"<h1>A blog post about Donuts</h1><p>Donuts, those delectable fried pastries, are a universally cherished indulgence that spans the spectrum from classic glazed rings to exotic, gourmet creations. These round confections symbolize the joy of sweet treats and the artistry of culinary imagination. Donuts offer an extraordinary range of flavors, textures, and toppings. From the fluffy and airy to the dense and cake-like, there's a donut for every craving. Whether savored as a morning delight with a cup of coffee, enjoyed as a dessert, or transformed into unique dessert hybrids, donuts are a beloved staple in the world of pastry. Their adaptability knows no bounds, with limitless combinations of dough, fillings, and toppings. The world of donut-making celebrates both timeless recipes that have delighted generations and boundary-pushing innovations that elevate the donut to an art form. Donuts represent more than just a confection; they embody a universal language of happiness and culinary creativity, uniting people and making every moment a little sweeter.</p><h2>The History of Donuts</h2><p>The history of donuts is an epic journey that traces its origins to Dutch settlers in 18th century America, where these 'olykoeks' or 'oily cakes' were initially crafted. Over time, donuts evolved into the sweet, fried delights we adore today, taking on various forms and flavors. The donut's worldwide journey began with European immigrants, and it soon became a symbol of American culture, earning its place in breakfast menus, cafes, and fairs. Donuts have continued to evolve, embracing new ingredients and influences from around the globe. Today, they are enjoyed in countless variations, cherished by people of all ages as a sweet and satisfying treat.</p><ul><li><strong>Classic Glazed Donut:</strong> The timeless favorite, coated in a shiny, sugary glaze.</li><li><strong>Jelly-Filled Donut:</strong> A delightful surprise with a fruit-filled center.</li><li><strong>Gourmet Donut:</strong> A canvas for culinary innovation, adorned with exotic toppings and unique fillings.</li></ul>",
	],
	"status": [Post.ACTIVE, Post.ACTIVE, Post.ACTIVE, Post.ACTIVE, Post.ACTIVE, Post.INACTIVE],
	"creator": [ADMIN1, ADMIN1, ADMIN2, ADMIN3, ADMIN4, ADMIN5],
	"updater": [ADMIN1, ADMIN1, ADMIN2, ADMIN3, ADMIN4, ADMIN5],
}

SHIPPING_ADDRESSES = {
	"address": [
		# Customers
		"1600 Independence Avenue",
		"123 Sesame Street",
		"124 Bluestone Road",
		"13 Mockingjay Lane",
		"1337 Cyber Street",

		# Admins
		"485 Echo Base",
		"444 Yavin Base",
		"1111 Avengers Compound",
		"10880 Malibu Point"
		"15 Triskelion",
	],
	"city": ["Sacramento", "San Francisco", "Los Angeles", "Seattle", "Sacramento", "Seattle", "Los Angeles", "San Francisco", "San Francisco", "Sacramento"],
	"state": ["CA", "CA", "CA", "WA", "CA", "WA", "CA", "CA", "CA", "CA"],
	"country": ["U.S", "U.S", "U.S", "U.S", "U.S", "U.S", "U.S", "U.S", "U.S", "U.S"],
	"postal_code": ["95814", "94114", "90012", "98104", "95834", "98011", "90032", "94080", "94015", "95818"],
	"creator": [CUSTOMER1, CUSTOMER2, CUSTOMER3, CUSTOMER4, CUSTOMER5, ADMIN1, ADMIN2, ADMIN3, ADMIN4, ADMIN5],
	"updater": [CUSTOMER1, CUSTOMER2, CUSTOMER3, CUSTOMER4, CUSTOMER5, ADMIN1, ADMIN2, ADMIN3, ADMIN4, ADMIN5],
}


class Command(BaseCommand):
	help = (
		'Makes data for the following models; Post, Product, ProductImage, ShippingAddress, Cart, CartItem, Order. '
	)

	def create_products(self) -> list[Product]:
		products = []
		for i in range(len(PRODUCT['name'])):
			product = Product.objects.create(
				name=PRODUCT['name'][i],
				description=PRODUCT['description'][i],
				extra_description=PRODUCT['extra_description'][i],
				price=PRODUCT['price'][i],
				estimated_delivery_date=PRODUCT['estimated_delivery_date'][i],
				status=PRODUCT['status'][i],
				stock=PRODUCT['stock'][i],
				creator=PRODUCT['creator'][i],
				updater=PRODUCT['updater'][i],
			)
			product.created_at = date(2024, 1, i+1)
			product.save()
			product.create_stripe_product_and_price_objs()
			products.append(product)
		self.stdout.write("Products created.")
		return products

	def create_product_images(self, products: list[Product]) -> None:
		for product in products:
			image_paths = PRODUCT_IMAGE.get(product.name, [])
			for image_path in image_paths:
				with open(image_path, 'rb') as image_file:
					ProductImage.objects.create(
						product=product,
						image=File(image_file),
						creator=product.creator,
						updater=product.updater,
					)
		self.stdout.write("ProductImages created.")

	def create_posts(self) -> None:
		for i in range(len(BLOG_POSTS['title'])):
			Post.objects.create(
				title=BLOG_POSTS['title'][i],
				preview_text=BLOG_POSTS['preview_text'][i],
				content=BLOG_POSTS['content'][i],
				status=BLOG_POSTS['status'][i],
				creator=BLOG_POSTS['creator'][i],
				updater=BLOG_POSTS['updater'][i],
			)
		self.stdout.write("Posts created.")

	def create_shipping_addresses(self) -> None:
		for i in range(len(SHIPPING_ADDRESSES['address'])):
			ShippingAddress.objects.create(
				address=SHIPPING_ADDRESSES['address'][i],
				city=SHIPPING_ADDRESSES['city'][i],
				state=SHIPPING_ADDRESSES['state'][i],
				country=SHIPPING_ADDRESSES['country'][i],
				postal_code=SHIPPING_ADDRESSES['postal_code'][i],
				creator=SHIPPING_ADDRESSES['creator'][i],
				updater=SHIPPING_ADDRESSES['updater'][i],
			)
		self.stdout.write("ShippingAddresses created.")

	def create_carts(self) -> list[Cart]:
		carts = []
		for _ in range(2):  # repeat the loop twice
			for customer in customers:
				cart = Cart.objects.create(
					status=Cart.INACTIVE,
					shipping_address=customer.get_last_shipping_address(),
					creator=customer,
					updater=customer
				)
				carts.append(cart)
		self.stdout.write("Carts created.")
		return carts

	def create_cartitems(self, carts: list[Cart], products: list[Product]) -> None:
		# Wrapper for creating a CartItem
		def create_cartitem(cart, product, quantity, creator):
			CartItem.objects.create(
				cart=cart,
				product=product,
				quantity=quantity,
				original_price=product.price,
				creator=creator,
				updater=creator,
			)
		# Cart 1
		create_cartitem(carts[0], products[0], 10, customers[0])
		create_cartitem(carts[0], products[1], 5, customers[0])
		create_cartitem(carts[0], products[2], 1, customers[0])

		# Cart 2
		create_cartitem(carts[1], products[3], 5, customers[1])
		create_cartitem(carts[1], products[4], 2, customers[1])
		create_cartitem(carts[1], products[5], 10, customers[1])

		# Cart 3
		create_cartitem(carts[2], products[6], 1, customers[2])
		create_cartitem(carts[2], products[7], 2, customers[2])
		create_cartitem(carts[2], products[8], 1, customers[2])

		# Cart 4
		create_cartitem(carts[3], products[9], 1, customers[3])
		create_cartitem(carts[3], products[0], 5, customers[3])
		create_cartitem(carts[3], products[1], 4, customers[3])

		# Cart 5
		create_cartitem(carts[4], products[2], 4, customers[4])
		create_cartitem(carts[4], products[3], 2, customers[4])
		create_cartitem(carts[4], products[4], 5, customers[4])

		# Cart 6
		create_cartitem(carts[5], products[5], 4, customers[0])
		create_cartitem(carts[5], products[6], 3, customers[0])
		create_cartitem(carts[5], products[7], 2, customers[0])

		# Cart 7
		create_cartitem(carts[6], products[8], 5, customers[1])
		create_cartitem(carts[6], products[9], 1, customers[1])
		create_cartitem(carts[6], products[0], 4, customers[1])

		# Cart 8
		create_cartitem(carts[7], products[1], 1, customers[2])
		create_cartitem(carts[7], products[2], 10, customers[2])
		create_cartitem(carts[7], products[3], 2, customers[2])

		# Cart 9
		create_cartitem(carts[8], products[4], 3, customers[3])
		create_cartitem(carts[8], products[5], 7, customers[3])
		create_cartitem(carts[8], products[6], 3, customers[3])

		# Cart 10
		create_cartitem(carts[9], products[7], 2, customers[4])
		create_cartitem(carts[9], products[8], 3, customers[4])
		create_cartitem(carts[9], products[9], 1, customers[4])

		self.stdout.write("CartItems created.")

	def create_orders(self, carts: list[Cart]) -> None:
		statuses = [Order.PLACED, Order.SHIPPED, Order.DELIVERED, Order.CANCELED, Order.PLACED, Order.SHIPPED, Order.DELIVERED, Order.CANCELED, Order.DELIVERED, Order.DELIVERED]
		# 2018, 2020, 2021, 2021, 2021, 2022, 2023, 2024, 2024, 2024
		created_at = [
			datetime(2018, 1, 25, 0, 0), datetime(2020, 9, 10, 0, 0), datetime(2021, 3, 28, 0, 0),
			datetime(2021, 3, 20, 0, 0), datetime(2021, 12, 25, 0, 0), datetime(2022, 4, 5, 0, 0),
			datetime(2023, 5, 18, 0, 0), datetime(2024, 1, 15, 0, 0), datetime(2024, 1, 22, 0, 0),
			datetime(2024, 4, 10, 0, 0),
		]
		for i, cart in enumerate(carts):
			order = Order.objects.create(
				cart=cart,
				total_price=cart.get_total_cart_price(),
				status=statuses[i],
				creator=cart.creator,
				updater=cart.updater,
			)
			order.created_at = created_at[i]
			order.save()
		self.stdout.write("Orders created.")

	# Define logic of command
	def handle(self, *args, **options):
		self.stdout.write("----- Making data... -----")
		products = self.create_products()
		self.create_product_images(products)
		self.create_posts()
		self.create_shipping_addresses()
		carts = self.create_carts()
		self.create_cartitems(carts, products)
		self.create_orders(carts)
		self.stdout.write("----- Finished. -----")
