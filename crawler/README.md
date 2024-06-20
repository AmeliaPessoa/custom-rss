
---

# How to Create and Schedule an Apify Actor Using a ZIP File

This guide will walk you through the steps to create an Apify actor using your code from a ZIP file and schedule it to run daily at 00:30.

## Prerequisites
- An Apify account.
- The URL of the actor project code compressed into a ZIP file.

## Step-by-Step Instructions

### 1. Log in to Apify
Log in to your Apify account at [Apify Console](https://console.apify.com/).

### 2. Obtain Your Apify API Token
1. Click on the **Actors** tab in the left-hand menu.
2. Click the **API** button next to the **Develop new** button on the top right corner.
3. You will see an "API token" section with the default API token created on sign-up.
4. Click **Copy to clipboard** to copy your API token to use later.

![Copy to clipboard](https://dl.dropboxusercontent.com/scl/fi/ou65r58dbj04urichfgk8/image7.png?rlkey=kbystwkp7bbte9av5wl7stkok&st=3zh57c1r&dl=0)

### 3. Create a New Actor
1. Click on the **Develop new** button in the **Actors** tab.
2. Click on **View all templates** to select the **Empty Python project** and then choose **Use this template**.
3. After the actor is created, click on **Source type: Web IDE** to select the **Zip file** source type.

![Source type](https://dl.dropboxusercontent.com/scl/fi/nsu0egsjlup09pknxmq8p/image4.png?rlkey=4rxysztdqk4hi8ht9wsfssgpa&st=clnnd0ho&dl=0)

4. Enter the URL of the ZIP file: `https://www.dropbox.com/scl/fi/ow89u0quxbxok86xxh5wo/DaCorunaApifyActor.zip?rlkey=ksox53s6rfgydnt6s645g80k8&st=9t1kf2ue&dl=1`.
5. On the bottom left corner of the actor page, click **Save & build**.

![Save & build](https://dl.dropboxusercontent.com/scl/fi/690oe8xhvhx6b5hx9hybl/image2.png?rlkey=iltrvw3rbx9ok4kxb3lucagsa&st=3ykcvevg&dl=0)

### 4. Schedule Your Actor
1. Navigate to the **Schedules** tab in the left-hand menu.
2. Click **Create new**.
3. Set the schedule to run the actor daily at 00:30.

#### 4.1. Creating a Schedule
- **Name**: You can provide a name for the schedule (optional).
- **Cron Expression**: Use `30 0 * * *` to run the actor every day at 00:30. It should be like this:

![Cron Expression](https://dl.dropboxusercontent.com/scl/fi/4kqczz3j0vbhyg2ee3yty/image8.png?rlkey=xyld6cyoye0amifiodgd5l4p3&st=u3hpkg4d&dl=0)

- **Timezone**: Select your local timezone.
- **Actor**: On the bottom of the page click on **Add** to select your actor.

![Select Actor](https://dl.dropboxusercontent.com/scl/fi/iccqpwmknh5af4h0n8il5/image3.png?rlkey=twhmsm3j304uin5nkz97iha52&st=w2v8z5i7&dl=0)

- **Input**: Enter the content of your `dacoruna.json` from the input folder in the ZIP file.
  - Replace `"your_apify_api_token"` with the token you obtained in Step 2.
  ```json
  "apify": {
      "api_token": "your_apify_api_token"
  }
  ```

Here's an example:

![Input Example](https://dl.dropboxusercontent.com/scl/fi/5aritb9xg9ajv2ok7gplc/image1.png?rlkey=ejpg70csj652irsmd7jpxfzb6&st=efrvoxnk&dl=0)

- **Enable**: Save the input and make sure to click on **Save & Enable** on the schedule.

![Save & Enable](https://dl.dropboxusercontent.com/scl/fi/yj3ze5tn1071qdw7uc0bc/image6.png?rlkey=b01drb7dok8a0uwismrkbm81x&st=b1m98dc3&dl=0)

### 5. Verify the Schedule
Ensure that the schedule is listed and enabled in the Schedules tab. Your actor should now run automatically every day at 00:30.

![Schedule](https://dl.dropboxusercontent.com/scl/fi/iahzn5j8zjfufh6ub16fa/image5.png?rlkey=ecfxc2lndqx7e4yrbsr2pjgj8&st=dxzj4ahu&dl=0)

---
