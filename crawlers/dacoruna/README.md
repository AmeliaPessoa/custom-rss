
---

# How to Create and Schedule an Apify Actor Using a GitHub Repository

This guide will walk you through the steps to create an Apify actor using your code from a GitHub repository and schedule it to run daily at 00:30.

## Prerequisites
- An Apify account.
- The link of the GitHub repository containing the actor project code.

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
2. On **From existing source code** select **Link Git Repository** and then choose **GitHub**.
3. Sign in to your GitHub account.
4. Link the GitHub repository with your code.

![Pick a repository from GitHub](https://www.dropbox.com/scl/fi/7z556c2fvprjwfnm03hhe/link-repository.png?rlkey=nb614djrywki5396zj6r5dwp2&st=0k4pjrjv&dl=0)

5. Enter the folder of your crawler on main branch: 

![Choose folder](https://www.dropbox.com/scl/fi/1ggskgi3fee7cvsths9pl/branch-folder.png?rlkey=h3zeiwsq1xz0nuhxwoch4m76a&st=agu6k8z5&dl=0)

6. On the bottom left corner of the actor page, click **Save & build**.

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

- **Input**: Choose JSON input, enter the content of your file `dacoruna.json` from the input folder in the repository.

- **Enable**: Save the input and make sure to click on **Save & Enable** on the schedule.

![Save & Enable](https://dl.dropboxusercontent.com/scl/fi/yj3ze5tn1071qdw7uc0bc/image6.png?rlkey=b01drb7dok8a0uwismrkbm81x&st=b1m98dc3&dl=0)

### 5. Verify the Schedule
Ensure that the schedule is listed and enabled in the Schedules tab. Your actor should now run automatically every day at 00:30.

![Schedule](https://dl.dropboxusercontent.com/scl/fi/iahzn5j8zjfufh6ub16fa/image5.png?rlkey=ecfxc2lndqx7e4yrbsr2pjgj8&st=dxzj4ahu&dl=0)

---
