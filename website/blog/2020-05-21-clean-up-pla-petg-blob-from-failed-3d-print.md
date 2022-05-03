---
title: How to clean up a PLA / PETG blob from a failed 3D print
author: Wade Norris
author_url: https://wnorris.github.io/
author_image_url: https://www.thespaghettidetective.com/img/wade.jpg
description: Don't replace it. Fix it! Rescue your 3D printer nozzle with the tools you can find in your toolbox.
tags: ['3D Printing Tips', 'How-To']
---

So you went to sleep with your 3D printer running. Excitedly, you wake up and run to go take a look at your beautiful new creation. To your dismay, something has gone horribly wrong. You’ve had a failed 3D print. It didn’t just create a fresh plate of filament spaghetti, but it has fully encased the hot end of your extruder in a PLA / PETG blob.

![](/img/blogs/failed-cleanup-1.png)

We’ve been there -- the racing heart, the panic, the fear your 3D printer will never run again. While it is possible you’ve damaged the 3D printer, it’s more likely you can get everything back to normal working order by following these steps. The most important part in 3D print clean up is to stay cool and don’t rush. Damage is more often caused by frustration and impatience when trying to pull off the cold hardened PLA / PETG blob with force than by the print failure itself.

<!-- truncate -->

## Step 1) Heat up the extruder

Bring the hot end up to temperature, this will melt the plastic solidified against the hot end and make it much easier to remove.

![](/img/blogs/failed-cleanup-2.png)

Pick a temperature that matches the material you were using when the failure occurred. Usually you’ll want to add about 30 degrees Celsius to the original print temperature since you’re trying to melt material on the outside of the heat block and not just inside of the extruder. One option if you want to play it extra safe is to start at the print temperature and work your way up. If you’re feeling resistance removing pieces of plastic from the hot end, bump the temperature a bit and try again.

To set the temperature to a specific setting use the following menu items:

* **Prusa MK3:** Settings -> Temperature -> Nozzle
* **Ender 3:** Control -> Temperature -> Nozzle

## Step 2) Use pliers to remove the blob

Grab a pair of pliers and gently remove blobs of plastic from the extruder. If you are successfully melting the contact points, the plastic pieces should almost fall off without any force. Using pliers is important because you may have globs of molten plastic dripping. Doing this with your hand is unsafe and can result in getting burned!

![](/img/blogs/failed-cleanup-3.png)

Be careful around the thermistor cables, these don’t get heated by the hot end and if a glob of plastic is attached to them it can be tempting to rip it off. These are some of the most delicate parts and can easily be damaged if you tug too hard. If you’re having trouble melting plastic attached to the thermistor cables, consider using the pliers to press this area into the heat block to help melt the plastic and make it easier to remove. It also may be tempting to snip at the plastic with cutters, but doing this near obscured cables is very risky. You may snip something you did not intend. Try the melting technique before you move to more aggressive strategies.

If you have a heat gun you can also melt the plastic in this targeted area. Keep in mind that you might have other plastic parts on your hot end that you don’t want to warp. Consider taking them off first if your mess requires heat gunning near them.

## Step 3) Use a brass brush to get the last bits

Once you’ve removed the large chunks of plastic, finish the 3D print clean up with a brass brush. Rubbing the brass brush on the heat block and other areas with leftover plastic will help gather up and pull off remaining bits of molten plastic.

![](/img/blogs/failed-cleanup-4.png)

Give some extra focus to the extruder nozzle area or consider completely replacing it. They are cheap and left over plastic in this area can cause future prints to want to curl up along the extruder, coalescing on the heat block instead of sticking to the bed.

Another trick here is to lower the temperature below the melting point for the material you were using. In this transition range, it will be bendy but not fluid. Grabbing parts of the plastic at this temperature may make it peel off in larger chunks like a plastic wrap. We’ve found 110-150 C to work well for PLA. Play around with it and see what works for you!

## Step 4) Recalibrate your printer and give it a test run

With the tugging, some parts may have shifted and it may be worth running a quick recalibration and re-leveling of the bed. At this point you should be able to run a test print. If all went well you’re back in working order!

Some items to look out for when running your test print:

* If you have plastic elements on your hot end, they may have cracked, melted, or warped during the attack of the molten glob. Consider re-printing these items if any seem damaged in a way that may interfere with your prints.
* If there was a major collision during the print failure, or you tugged too hard on a blob trying to get it off, it’s possible to bend or loosen the heat break (the part between the heat block and the heatsink). Keep an eye out for filament oozing out from above the heat block.
* If filament is pulling back up along the outside of the extruder nozzle rather than sticking to the bed, it may be small amounts of leftover plastic trying to coalesce with the extruded filament. Try cleaning up the nozzle with the wire brush. Personally I find the brass nozzles are so cheap it’s easier to just replace it than clean it!

## Step 5) Sign up for The Spaghetti Detective

Consider using [The Spaghetti Detective](http://www.thespaghettidetective.com/) to monitor and catch your failed 3D print early. With The Spaghetti Detective, an AI algorithm carefully monitors your print and will send you alerts when it looks like a failed 3D print has occurred. The system can even pause your print for you while you’re asleep, potentially saving you from waking up to a huge mess, or worse, a damaged printer!

![](/img/blogs/failed-cleanup-5.png)
