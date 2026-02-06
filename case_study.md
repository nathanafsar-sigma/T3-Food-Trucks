Case Study: Food Trucks
large Food Trucks

Tasty Truck Treats (T3) is a catering company that specializes in operating a fleet of food trucks in Lichfield and its surrounding areas. The company is dedicated to providing delicious and diverse culinary experiences to its customers. T3 takes pride in its fleet of food trucks, each of which operates semi-independently. This means that each truck has its own unique menu and style, offering a variety of delectable treats to cater to different tastes and preferences. From gourmet burgers and sandwiches to mouthwatering desserts and refreshing beverages, T3 aims to satisfy a wide range of culinary cravings.

The company's food trucks are strategically stationed at popular locations throughout Lichfield and the surrounding area, ensuring maximum visibility and accessibility to potential customers. These locations could include bustling city areas, office complexes, event venues, and other areas with high foot traffic.

T3's food trucks are designed to be eye-catching and inviting, featuring vibrant branding, enticing menu displays, and friendly staff members. The company believes in delivering not only delicious food but also exceptional customer service, creating a memorable dining experience for every customer they serve.

While each food truck operates independently on a day-to-day basis, T3 collects overall sales data from each truck every few hours, giving an overall view of how their fleet is performing.

Currently, the data is stored in an RDS running MySQL on AWS, and the trucks are responsible for uploading their data to the database. This architecture has been suitable so far but relatively high costs have meant they want to complete a data migration project to move to a new architecture. The chosen architecture is one of a 'Data Lake' which will cut costs whilst still ensuring the data is accessible and usable.

The Brief
Hosting their data on AWS has been a great success for T3, but the costs of running an RDS instance have been steadily increasing. The company is looking to migrate their data to a new architecture that will be cheaper to run, and more flexible in terms of the types of data they can store.

The process will be two step:

Historical Data Migration: Move all of the existing data from the RDS instance to the new architecture.
Periodic Data Migration: Every three hours new data will end up in the database, this will need to be processed and uploaded to the data lake.
We'll be completing this work over the next two weeks.

Stakeholders
For this project, we have three internal stakeholders.


Hiram Boulie
Chief Financial Officer
As CFO, Hiram has responsibility for all financial issues and processes at T3. He wants to ensure that the company is on track to be both stable and profitable over the next five years. T3 is currently in talks about being acquired by a national chain, and a robust financial outlook is a key element of those discussions.

Hiram has two priorities:

Cut costs
Raise profits

Miranda Courcelle
Head of Culinary Experience
Miranda's first job out of culinary school was working on a T3 truck, and she's worked her way up within the company to lead the CE team. She's a passionate believer in the importance of casual dining options for building a vibrant local community, and sees T3 as a big part of that for Lichfield.

Her role involves overall oversight of truck menus and locations, making sure that T3 products are appealing and affordable for all their customers. Understanding which cuisines/price points are in demand at which locations is a key part of her responsibilities.


Alexander D'Torre
Head of Technology
Alexander is responsible for all technology at T3, including the data architecture. He has a background in data engineering and is passionate about using technology to drive business success. He is keen to ensure that T3's data architecture is both cost-effective and scalable, and is excited about the potential of a data lake to meet these needs.

He is an opinionated person who has strong views on how the data architecture should be designed and implemented. He is keen to ensure that the data lake is built using best practices, but is open to new ideas and approaches.

The Task
Over the next two weeks, you're going to build the required reporting pipeline and deploy it to the cloud. In this first week, you'll focus on completing the data migration step from RDS to your solution. An ETL script will pull in the raw transaction data, process it, and store the cleaned data in a data warehouse. You'll also develop a dashboard that reads from the database for analysis.

fullwidth Architecture diagram

Separate Artefacts
You'll write a lot of code in this week, doing a lot of different-but-related tasks. By the end of the week, you should have created the following:

An extract Python script which downloads relevant data from the RDS
A transform Python script which creates the downloaded files, producing all the files we need to start in the data lake
A notebook which reads from the transaction data file, exploring and visualising the data.
An ETL pipeline task that runs locally, extracting transaction data from the RDS uploading it to the our data lake.
A cloud-based dashboard service that reads from the cloud database.
Crucially, although some of these artefacts will depend on the outputs of others, each script/task/notebook should run independently; building each one as a distinct element makes them more testable, more flexible, and more maintainable.

Tools & Tech Stack
Alexander D'Torre, T3's Head of Technology, has said the following:


Alexander D'Torre
Hi, @here; I've been reading up recently on data lakes and I think this is the way we should go. I've seen a few examples of people using AWS S3 for the storage layer, and Athena for querying the data. I think this is a good combination, as S3 is cheap and scalable, and Athena is easy to use and integrates well with S3.

Also, I'm absolutely deadset on using Docker and Terraform on this project as far as possible. We simply must be future proofing our architecture, and I think these tools are the way to do that. I've seen a few examples of people using Docker to containerize their ETL pipelines, and Terraform to manage their AWS infrastructure. I think this is a good combination, as Docker is easy to use and integrates well with Python, and Terraform is easy to use and integrates well with AWS.

I'm also keen to use Streamlit for the dashboard, as I've seen a few examples of people using it to create interactive dashboards. I think this is a good choice, as Streamlit is easy to use and integrates well with Python.

All other decisions, I'll leave up to you

Thanks, Allie

The Data
Initially, we'll use historical truck sales data to build our pipeline. This data is stored in a MySQL RDS instance, and is available for download via a URL supplied by the client.

Trucks ERD

The previous Data Engineering team decided to use a STAR schema to structure the data, you may not have come across this before but we'll work out how to work with it as we deeper into the challenge.