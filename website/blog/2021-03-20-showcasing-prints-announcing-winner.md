---
title: Showcasing Your Prints and Announcing a Giveaway Winner
author: Aaron Davidson
author_url: https://twitter.com/nexthoudini
author_image_url: https://www.thespaghettidetective.com/img/aaron.jpg
tags: ['The Spaghetti Detective Updates', 'Giveaway']
---

![](/img/blogs/userprints/mike_wise.jpg)

For the past several weeks, since we [announced the giveaway](https://www.thespaghettidetective.com/blog/2021/02/27/bringing-the-detective-to-life/), The Spaghetti Detective's community has responded to the challenge with enthusiasm and creativity. More people than we ever expected printed [Wekster's awesome model](https://www.patreon.com/posts/spaghetti-48229606) and tagged us and Wekster, and because we have such an involved, enthusiastic community, we have given out thousands of free Detective Hours. We love all of the prints, but after the jump are a few of my personal favorites, along with the winner announcement and winner selection process.

<!--truncate-->

## Look at what you've done

First, there's the page header image, shared by [Mike Wise](https://www.instagram.com/p/CMUm5IGnBi3Pz747R7_y7CcmSEa59LCGWskk_U0/) on Instagram. He printed the bust in white and then painted it, to really cool effect.

![](/img/blogs/userprints/steve_lionel.jpg)

Then, there's [Steve Lionel](https://www.facebook.com/steve.lionel.7/posts/4117557678276674) from Facebook, who separated the singlecolor model himself using [Mosaic's Canvas](https://www.mosaicmfg.com/products/canvas) and [BigBrain3D's simplycolor3d](https://www.bigbrain3d.com/product/simplycolor3d-software-to-make-any-3d-print-multicolor/) and displayed The Detective next to fellow sleuth Veronica Mars.

![](/img/blogs/userprints/janner_breeze-crow.jpg)

[Janner Breeze-Crow](https://twitter.com/breeze_crow/status/1366870226810331141) put sunglasses on her print.

![](/img/blogs/userprints/alex_gorzen.jpg)

[Alex Gorzen](https://twitter.com/Zeusandhera/status/1366252376659746818) painted his eyes and brim with a paint marker.

![](/img/blogs/userprints/chieF.jpg)

[cheiF](https://twitter.com/sp3cialk/status/1366820161257373701) printed the full-multicolor version using a fittingly noir grayscale color palette.

![](/img/blogs/userprints/sakja_teda.jpg)

And, as [SakJa Teda](https://twitter.com/SakJaTeda/status/1368888338690801669) shows, the model is every bit as beautiful in singlecolor. I'm featuring SakJa's here just because I really like the offbeat but beautiful filaments in this one.

Check out [our facebook page](https://www.facebook.com/thespaghettidetective), [our twitter page](https://twitter.com/thespaghettispy), and [our instagram tags](https://www.instagram.com/the.spaghetti.detective/tagged/) for more user prints. We got a lot and can't feature them all here, but we're flattered by and appreciative of every one of them.

## Choosing a winner

This is not a contest. It's a giveaway. I wanted to make sure that we chose a winner in a fair, random way that I had no sway over.

I overengineered the random picker.

First, I grabbed the list of TSD emails from the spreadsheet I've been using to keep track of and follow up with giveaway participants. I stuck them in a python set to ensure uniqueness, then made the set a list (to ensure the order would stay the same) and grabbed the length of that list.

I plugged that length in as the upper bound on [random.org](https://www.random.org/integers/?mode=advanced), which I had generate 10,000 integers between 1 and the list length. The website is a true random number generator. It uses atmospheric noise for the random generation, instead of the pseudorandom generator most programming languages have built in.

At this point, I had a collection of 10,000 numbers, and I needed to see which appeared the most times. I wrote a quick python function calculate the top five most-frequently-occurring values in the numbers list, along with how many times they occur. There was a clear winner, with three more occurrences than any other index: Number 16. That number corresponded to

## The winner

![](/img/blogs/userprints/jussi_hintsala.jpg)

I'm thrilled to announce that [Jussi Hintsala](https://twitter.com/Jussihin/status/1367227633168171009?s=19) has won twelve free months of The Spaghetti Detective's Pro tier with unlimited Detective Hours. Thank you all for participating and for helping us celebrate 50,000 users. We hope to do something just as special for you guys when we've got 50,000 more. We wish you safe, happy printing watched over by The Spaghetti Detective.
