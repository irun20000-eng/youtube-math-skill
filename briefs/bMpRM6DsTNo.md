---
schema: yt-brief/v1
video_id: bMpRM6DsTNo
url: https://www.youtube.com/watch?v=bMpRM6DsTNo
title: "How Many People Were Really in This Poll? | The Farey Sequence"
channel: "Kia Keng's nerd folder"
published: 2026-10-11
duration_sec: 1567
duration: "26:07"
playlist: 일단모아
route: math
route_reason: "수학 키워드('수열')"
transcript_lang: en
transcript_kind: auto
transcript_tracks: "ar(auto), bn(auto), nl(auto), en(auto), fr(auto), de(auto), iw(auto), hi(auto), id(auto), it(auto), ja(auto), ko(auto), ml(auto), pl(auto), pt(auto), pa(auto), ru(auto), es(auto), ta(auto), te(auto), uk(auto)"
transcript_lines: 580
transcript_chars: 25759
collected_at: 2026-10-16T08:32:17+09:00
collector: aside/yt-brief-collector v1
---

## 영상 설명

A headline says 72.7% of people surveyed said yes. How many people could that be, at the very least? Not a thousand, not a hundred: just 11, because 8 out of 11 is 72.727…%.

Finding that number is a surprisingly deep problem: given a narrow window of decimals, find the fraction with the smallest denominator inside it. The answer comes from the "wrong" way to add fractions (add the tops, add the bottoms: the mediant) and from a curious list of fractions that a geologist, John Farey, wrote about in 1816.

Following that one idea takes us through:
• why neighbouring Farey fractions a/b and c/d always satisfy bc − ad = 1, proved with a picture of grid points
• a walk of mediants that lands on the simplest fraction, and why it can never skip it
• why 38.2% leads to the Fibonacci numbers, and why 99.9% needs at least 667 people
• Ford circles: one circle for every fraction, and no two ever overlap
• the Stern–Brocot tree, which contains every positive fraction exactly once
• the best fractions for π, and why nothing beats Zu Chongzhi's 355/113 until 52163/16604
• the 6/π² ≈ 61% chance that two whole numbers share no common factor
• how the spacing of the Farey fractions is tied to the Riemann hypothesis

Chapters
0:00 How many people were in the poll?
1:29 The problem
3:38 Farey's curious property
6:53 Fractions as points
10:19 Walking to the answer
13:38 Ford circles
16:19 A tree of every fraction
20:04 How many fractions?
22:40 A million-dollar question
24:51 Epilogue

Try it yourself: a poll says 33.3%. That could be just 3 people (1 out of 3). Change one digit to 33.4%, and the smallest possible poll is 287 people.

Every claim in the video is proved or attributed to its source, and every number on screen was recomputed by computer. The Farey discrepancy values in the "million-dollar question" chapter are computed data, not a theorem: the Riemann hypothesis is still open.

Sources and further reading
• J. Farey, "On a curious property of vulgar fractions", Philosophical Magazine 47 (1816)
• A.-L. Cauchy, "Démonstration d'un théorème curieux sur les nombres" (1816)
• C. Haros, tables for converting decimals into the simplest ordinary fractions, Journal de l'École Polytechnique 4 (1802)
• M. A. Stern, Journal für die reine und angewandte Mathematik 55 (1858); A. Brocot, Revue Chronométrique 3 (1861)
• L. R. Ford, "Fractions", American Mathematical Monthly 45 (1938)
• J. Franel and E. Landau, Nachrichten der Gesellschaft der Wissenschaften zu Göttingen (1924)
• N. Brown and J. Heathers, "The GRIM test", Social Psychological and Personality Science (2017)
• R. Graham, D. Knuth, O. Patashnik, Concrete Mathematics, §4.5
• G. H. Hardy and E. M. Wright, An Introduction to the Theory of Numbers, ch. III

Animation made with Manim Community Edition. Narration: synthetic voice (Microsoft neural text-to-speech). Music and sound effects synthesised for this video.

#math #fareysequence #numbertheory

## 자막 (en, 자동생성)

> ⚠️ 원어가 한국어가 아니다. 자막은 원어 그대로다. 핵심 인용·발언은 원문을 그대로 인용하고 번역은 괄호로 덧붙인다(번역을 인용처럼 쓰지 말 것).

[00:00] Here's a headline. [music] 72.7%
[00:03] of people surveyed said yes. It sounds
[00:06] like a big serious poll. Maybe a
[00:09] thousand people, maybe a 100. But here's
[00:13] a question we can actually answer. What
[00:16] is the smallest number of people that
[00:18] could have produced this exact number?
[00:20] [music]
[00:20] Think about it. With 10 people, the
[00:23] possible percentages go up in steps of
[00:25] 10, 70, then 80. No good. with 20 people
[00:30] steps of five. 30 [music] 40 50 people
[00:34] still nothing rounds to 72.7.
[00:37] The answer is 11. 8 out of 11 is 72.727
[00:42] [music] repeating. 11 people and the
[00:45] headline is perfectly honest. And 11
[00:48] isn't a lucky guess. There's a beautiful
[00:51] almost mechanical way to find it for any
[00:53] percentage at all. 38.2% 2% at least 34
[00:58] people 99.9%
[01:02] at least 667.
[01:04] [music] The tool that does it is a
[01:06] curious list of fractions written down
[01:08] by a geologist in 1816.
[01:11] Follow it far enough and it leads to
[01:13] circles stacked along a line to the best
[01:15] approximations of pi to the chance that
[01:17] two numbers share no common factor and
[01:19] finally to the most famous unsolved
[01:21] problem in mathematics. This is the
[01:23] story of the fairy sequence and of the
[01:25] simplest fraction.
[01:29] [music]
[01:33] Let's state the problem carefully. A
[01:35] survey reports a percentage rounded to
[01:38] one decimal place. Behind it is a true
[01:41] fraction. P people said yes out of Q
[01:43] people in total. Rounding tells us where
[01:46] P over Q must lie. 72.7%
[01:49] means the true value is at least 72.65.
[01:52] 65% and less than 72.75.
[01:56] So P over Q lies in a window from 0.7265
[01:59] up to but not including 0.7275.
[02:03] We want the smallest Q for which some
[02:05] fraction P over Q lands in that window.
[02:08] In other words, among all the fractions
[02:10] in a given interval, we want the one
[02:12] with the smallest denominator.
[02:14] Let's call it the simplest fraction in
[02:16] the window. The obvious approach is
[02:19] brute force. Take Q= 1. The fractions 0
[02:22] and 1. Neither is in the window. Q
[02:26] equals 2 halves. No. Then third,
[02:30] quarters, fifths, and so on. Each row is
[02:33] a ruler with finer and finer marks. And
[02:36] we're waiting for a mark to fall inside
[02:37] a very narrow slot. Rows 1 through 10
[02:40] all miss. At Q= 11, 81 falls right into
[02:44] the slot. So the answer is 11. And brute
[02:48] force found it. But brute force needs
[02:50] one row for every denominator up to the
[02:52] answer. For 99.9%
[02:55] that's 667
[02:57] rows. [music] Quoted as 99.999%
[03:01] and the answer jumps to 66,667.
[03:05] Every extra decimal place can multiply
[03:07] the work by 10. [music] We'd like a
[03:10] method that walks straight to the answer
[03:11] and a reason to trust that the answer is
[03:13] right. And this isn't only a puzzle.
[03:17] Researchers Nick Brown and James
[03:18] Heathers built a closely related check
[03:20] called the grim test and used it to flag
[03:22] averages and published psychology papers
[03:24] that could not have come from the sample
[03:26] sizes those papers reported. [music] To
[03:28] do better than brute force, we need to
[03:30] understand how fractions sit next to
[03:32] each other. And for that, we go back to
[03:35] 1816.
[03:41] In 1816, an English geologist named John
[03:44] Ferry sent a short letter to the
[03:45] philosophical magazine. Its title on a
[03:48] curious property of vulgar fractions.
[03:51] Vulgar just meant ordinary fractions
[03:53] like 3/4. Here's what he was looking at.
[03:57] Take every fraction from 0 to one whose
[03:59] denominator is at most n written in
[04:01] lowest terms and list them in increasing
[04:04] order. That list is called the fairy
[04:06] sequence of order n. [music] Order one
[04:09] is just zero and one.
[04:11] Order two adds 1/2. Order three adds 1/3
[04:15] and 2/3. Order four adds the quarters.
[04:18] And order five adds the fifths, giving
[04:20] 11 fractions in all. Now look at any
[04:23] three neighbors. Say 1/3, 2 fths, and
[04:26] 1/2. Add the outer numerators. 1 + 1 is
[04:30] 2. Add the outer denominators. 3 + 2 is
[04:34] 5. 2 fths. Exactly the fraction in the
[04:37] middle. Try another. Two- fifths. 1/2 3
[04:41] fifths. 2 + 3 over 5 + 5 is 510, which
[04:45] is 1/2. This always happens. [music] The
[04:49] middle of any three neighbors is what
[04:51] you get by adding the outer numerators
[04:53] and adding the outer denominators. This
[04:55] combination, the sum of the numerators
[04:57] over the sum of the denominators, is
[04:59] called the medant. Students are told
[05:02] it's the wrong way to add fractions, and
[05:04] it is. But it's a very good way to find
[05:06] a fraction between two others. If a over
[05:10] b is less than c over d, their median
[05:12] always lies strictly between them. In
[05:14] fact, this is how the sequence grows.
[05:17] Going from order four to order five,
[05:19] every new fifth appears as the median of
[05:21] its two neighbors. 1/5 between 0 and
[05:25] 1/4. Two- fifths between 1/3 and 1/2.
[05:30] 3- fifths between 1/2 and 2/3. And 4
[05:33] fths between 3/4 and 1. Ferry didn't
[05:37] prove his property. That same year,
[05:40] Augustine Lewis Koshi did and it later
[05:43] turned out that a French mathematician
[05:44] Charles Aras had founded 14 years
[05:47] earlier in 1802 while making tables for
[05:49] turning decimals into ordinary fractions
[05:52] which is almost exactly our problem.
[05:55] [music] Behind all of this is a single
[05:57] identity. If a over b and c over d are
[06:00] neighbors in a fairy sequence, then b *
[06:02] c minus a * d equals 1. Cross multiply.
[06:06] Subtract [music] and you always get
[06:08] exactly 1. Check it. 1/3 and 2 fths 3 *
[06:12] [music] 2 - 1 * 5 is 1. 2 fths and 1/2 5
[06:17] * 1 - 2 * 2 1 again. And fair's property
[06:21] drops right out of it. [music] Say a
[06:24] over b, p over q and c over d are three
[06:26] neighbors in a row. Then b * p minus a *
[06:30] q is 1 and c * q - d * p is 1. Set the
[06:34] two equal. collect terms and p over q= a
[06:37] + c over b + d the medant. But why
[06:41] should b * c minus a * d always be 1?
[06:44] You can prove it by induction with
[06:46] algebra. [music]
[06:47] There's a far more beautiful reason and
[06:49] it's hiding in a grid of points.
[06:56] Draw a grid of points with whole number
[06:58] coordinates. Put denominators along the
[07:01] horizontal axis and numerators up the
[07:03] vertical one. Then the fraction P over Q
[07:06] becomes the point Q comma P and its
[07:08] value is the slope of the line from the
[07:10] origin to that point. Equal fractions
[07:13] lie on the same line. 1/2 2/4 and 36s
[07:17] all sit on the line of slope 1/2. The
[07:20] fraction in lowest terms is the first
[07:21] point that line hits. Call these the
[07:24] visible points. Stand at the origin and
[07:27] look out. They're the points you can
[07:29] see, not hidden behind another point.
[07:31] Now, the fairy sequence has a lovely
[07:33] picture. Keep only denominators up to n.
[07:36] The points in this triangle. Sweep array
[07:39] from the floor, slope zero, up to the
[07:41] diagonal, slope one. The visible points
[07:44] it touches in order are exactly the very
[07:47] sequence of order n. Take two neighbors
[07:50] a over b and c over d. There are two
[07:53] points and the origin form a triangle.
[07:55] Since they're neighbors, the sweep goes
[07:57] from one to the other without touching
[07:59] anything in between. And any grid point
[08:01] inside this triangle would have a
[08:03] denominator of at most n and a slope in
[08:05] between. So the sweep would have hit it.
[08:08] The triangle contains no grid points
[08:10] apart from its three corners. Double the
[08:12] triangle into a parallelogram with its
[08:15] fourth corner at B plus D, a plus C.
[08:18] It's empty too. Apart from its corners,
[08:21] the second half is just the first half
[08:23] turned around its center. Now copy this
[08:25] parallelogram, sliding it along its own
[08:27] sides. The copies tile the whole plane
[08:30] with no gaps and no overlaps. And each
[08:32] copy owns exactly one grid point at its
[08:35] corner. Here's the key. The grid has
[08:38] exactly one point per unit of area.
[08:41] Since each tile owns exactly one point,
[08:44] each tile must have an area of exactly
[08:46] one. And the area of a parallelogram
[08:48] with sides B comma A and D comma C is
[08:51] the determinant B * C minus A * D. So B
[08:55] * C minus A * D equals 1. Fair's
[08:58] property proved by a picture. Look at
[09:01] that fourth corner again. B plus D comma
[09:04] A plus C. That's the [music] median. The
[09:07] median of two neighbors is the far
[09:09] corner of their parallelogram. [music]
[09:11] And now we can see why the median is
[09:13] special. Any fraction strictly between A
[09:16] over B and C over D is a grid point
[09:18] strictly inside the wedge between their
[09:20] two rays. Because the parallelogram
[09:23] tiles the grid, that point equals U
[09:25] copies of the first side plus V copies
[09:27] of the second, where U and V are whole
[09:29] numbers and both are at least one. Its
[09:31] denominator equals U * B + V * D, which
[09:35] is at least B plus D. And it equals B
[09:37] plus D only when U and V are both one at
[09:40] the median itself. If you prefer
[09:42] algebra, here's the same argument in one
[09:44] line. For a fraction P over Q strictly
[09:47] between them, b * P minus A * Q is a
[09:50] positive whole number. And so is C * Q -
[09:52] D * P. So each is at least 1. [music]
[09:56] And Q= B * the 2 plus D * the first. So
[10:00] Q is at least B + D. Let's write down
[10:03] what we've earned. Between two fairy
[10:06] neighbors, the median is the simplest
[10:08] fraction. It has the smallest
[10:10] denominator and it's the only fraction
[10:12] in between with that denominator.
[10:15] That is exactly the tool our survey
[10:17] problem needs.
[10:22] Back to our window from 0.7265
[10:25] to 0.7275.
[10:28] Start with the two simplest fractions.
[10:30] There are 0 over one on the left and 1
[10:32] over one on the right. Their neighbors 1
[10:35] * 1 - 0 * 1 is 1. and the window sits
[10:39] between them. Here's the rule. Take the
[10:43] medant. [music]
[10:44] If it lands in the window, stop. That's
[10:46] the answer. If it's to the left of the
[10:49] window, it becomes the new left end. If
[10:52] it's to the right, it becomes the new
[10:53] right end. Then repeat. The median of 0
[10:57] over 1 and 1 / 1 is 1/2. Too small. So
[11:01] 1/2 becomes the left end. 1/2 and 1 give
[11:05] 2/3.
[11:06] Still too small.
[11:08] 2/3 and 1 give 3/4. Too big, so 3/4
[11:13] becomes the right end. 2/3 and 3/4 give
[11:16] 57th.
[11:18] Too small. 57th and 3/4 give 8 11ths.
[11:22] 0.72727.
[11:25] Inside,
[11:26] five [music] steps and we have our 11
[11:28] people. Why is this right? Each step
[11:32] replaces one end by the median and the
[11:34] new pair are still neighbors. B * C
[11:36] minus A * D is still one. So at every
[11:39] moment, the window sits strictly between
[11:41] two neighbors. And every fraction
[11:43] strictly between neighbors has a
[11:45] denominator of at least B plus D, the
[11:47] median's denominator. So the first
[11:50] median to land in the window has the
[11:52] smallest denominator possible. Nothing
[11:54] simpler was skipped, and the walk must
[11:57] stop because the denominators grow at
[11:59] every step, but can never pass the
[12:01] answers. Try 38.2%.
[12:05] The walk goes 1/2, 1/3, 2 fths, 3/8,
[12:08] 513, 8 21sts, and lands on 1334ths.
[12:13] Fibonacci numbers left, [music] right,
[12:16] left, right. 38.2% is close to 1 minus
[12:20] one over the golden ratio, and the
[12:21] golden ratios walk zigzags forever
[12:24] through ratios of neighboring Fibonacci
[12:26] numbers. [music] So, at least 34 people.
[12:29] Now, try 99.9%.
[12:32] 1/2 too small. 2/3 too small. 3/4
[12:38] fifths. 56ths. Too small. Too small. Too
[12:41] small. The walk creeps towards one and
[12:44] needs 666 steps to reach 666 over 667.
[12:50] Correct. But slow. But look, all of
[12:53] those steps went the same way. If the
[12:56] walk moves right k times in a row, the
[12:58] left end becomes a plus k c over b plus
[13:00] k d. So instead of stepping, we can
[13:03] solve for the largest k that keeps us
[13:05] left of the window and jump. For 99.9%,
[13:09] that's a single jump. Grouping the walk
[13:11] into runs like this is Uklid's
[13:13] algorithm, the ancient method for
[13:15] greatest common divisor. And the run
[13:17] lengths are the terms of a continued
[13:18] fraction. The number of jumps grows only
[13:21] like the logarithm of the answer. So
[13:23] even a window a billion times narrower
[13:25] takes a few dozen jumps at most. So we
[13:28] have an algorithm and a proof that it's
[13:30] right. But the walk deserves a better
[13:32] picture. [music] In 1938, Lester Ford
[13:36] found one.
[13:41] For every fraction P over Q in lowest
[13:43] terms, draw a circle resting on the
[13:45] number line at P over Q with a diameter
[13:47] of 1 / Q ^2. Lester Ford described these
[13:51] in 1938 and they're now called Ford
[13:53] circles. The circles at zero and at 1/2
[13:56] have diameter 1. The circle at 1/2 has
[14:00] diameter 1 quarter. Thirds get 1 nth
[14:03] quarters 1/16th and so on. The simpler
[14:05] the fraction, the bigger its circle. Now
[14:08] something remarkable happens. These
[14:11] circles never overlap. Any two of them
[14:14] either just touch or don't meet at all.
[14:16] and two circles touch exactly when their
[14:18] fractions are fairy neighbors. The proof
[14:21] is one calculation. Take the circles at
[14:24] A over B and C over D. Compare the
[14:26] squared distance between their centers
[14:28] with the square of the sum of their
[14:29] radi. Almost everything cancels and the
[14:32] difference is this. B * C - A * D^ 2 - 1
[14:36] all over B ^ 2 D^ 2. The top is a whole
[14:40] number squared minus one. So, it's never
[14:42] negative. The circles never overlap. And
[14:45] it's zero. So the circles touch exactly
[14:47] when B * C minus A * D is plus or minus
[14:50] one. So between two touching circles
[14:53] there's a gap shaped like a curved
[14:54] triangle. The biggest ford circle and
[14:57] that gap belongs to the median and it
[14:59] touches both. Zoom in and the pattern
[15:02] repeats at every scale. Between any two
[15:04] touching circles sits the median circle.
[15:06] Then smaller circles and the smaller
[15:08] gaps forever. Now our survey problem has
[15:11] a picture. Mark the window on the line.
[15:14] Among the circles standing inside it,
[15:17] the simplest fraction has the biggest
[15:19] circle. So the question becomes, what is
[15:22] the largest circle in the window?
[15:24] Zooming in on 0.7265
[15:26] to 0.7275,
[15:28] there it is. The circle of 811s towering
[15:31] over everything else in the window. And
[15:33] the median walk becomes a walk down
[15:35] through the circles from the circles at
[15:38] 0 and 1 to 1/2, then 2/3, 3/4, 57th, and
[15:42] 8 11ths. Each new circle sits in the gap
[15:45] between the two circles that hold the
[15:47] window. Ford circles also tell us
[15:50] something about approximation.
[15:52] Draw a vertical line through any
[15:53] irrational number. On its way down, it
[15:56] must pass through infinitely many
[15:58] forward circles. And if it passes
[16:00] through the circle at P / Q, then P over
[16:03] Q is within 1 / 2 Q ^2 of the number.
[16:06] [music] So every irrational number has
[16:08] infinitely many unusually good
[16:09] fractional approximations
[16:12] which raises a natural question for a
[16:15] number like pi. Which fractions are the
[16:17] best ones? [music]
[16:22] So far we've stayed between 0 and 1.
[16:25] Let's lift that limit. Start with 0 over
[16:29] 1 and 1 / 0. 1 / 0 isn't a number but
[16:33] treat it as infinity. the fraction at
[16:35] the far end of the line. Their median is
[16:38] one over one. Now keep inserting medians
[16:41] between every pair of neighbors again
[16:43] and again. Arrange the new fractions by
[16:45] the generation they appear in and
[16:47] connect each one to the fraction it came
[16:49] from. You get a binary tree, one at the
[16:53] top, then 1/2 and two, then 1/3, 2/3,
[16:57] [music] three halves, and three, and so
[17:00] on forever. This tree contains every
[17:03] positive fraction exactly once already
[17:06] in lowest terms. Every fraction shows up
[17:09] because the median walk can find any
[17:11] target. Nothing repeats because reading
[17:14] the tree from left to right puts the
[17:15] fractions in order of size. And each one
[17:18] is in lowest terms because B * C minus A
[17:21] * D is one. It's called the Stern Broco
[17:24] tree. [music] The German mathematician
[17:26] Moret Stern described it in 1858.
[17:29] Ashel Broco, a French clock maker,
[17:31] founded independently in 1861 for a very
[17:34] practical reason, designing gear trains.
[17:37] Two meshing gears turn at a ratio set by
[17:40] their numbers of teeth, and teeth cost
[17:41] money. So, he needed simple fractions
[17:44] close to awkward ratios. The same
[17:47] question as our survey. Every number has
[17:50] a path down this tree. At each fraction,
[17:53] go left if the number is smaller and
[17:55] right if it's bigger. A rational number
[17:57] eventually lands on itself and stops. An
[18:00] irrational number goes on forever. Let's
[18:03] follow pi. Pi is bigger than one, so go
[18:07] right. Bigger than two, right, bigger
[18:10] than three, right. Smaller than four,
[18:13] left. Then 7 halves, 10/3, [music] 13/4,
[18:17] 16 fths, 196s, and 227ths. Left every
[18:21] time. [music] Seven lefts in a row
[18:24] ending at 227th. the approximation many
[18:26] of us learned at school. Then 15 rights
[18:29] ending at 333 over 106.
[18:33] Then a single left at 355 over 113.
[18:38] And then 292 rights in a row. 3 7 15 1
[18:44] 22.
[18:46] These run lengths are the continued
[18:48] fraction of pi. [music]
[18:50] = 3 + 1 over 7 + 1 over 15 + 1 over 1 +
[18:54] 1 over 292 and so on. The walk and the
[18:58] continued fraction are the same thing,
[19:00] which is why grouping the walk into runs
[19:02] gave us that speed up. [music] Here's
[19:04] the remarkable part. Call a fraction a
[19:07] record if it's closer to pi than every
[19:08] other fraction with the same or a
[19:10] smaller denominator.
[19:12] Every record lies on pi's path through
[19:14] the tree. The reason is the same
[19:16] argument as before. A fraction off the
[19:19] path is separated from pi by a median on
[19:22] the path. [music] That median has a
[19:24] smaller denominator and it's closer to
[19:26] pi. So look at 355 over 113.
[19:31] It agrees with pi to six decimal places.
[19:35] The Chinese mathematician Zu Chongji
[19:37] found it in the fifth century. Right
[19:39] after [music] it, Pi's path crawls 292
[19:42] steps in a single direction. Those steps
[19:44] are the only candidates to beat it. And
[19:46] they creep forward so slowly that the
[19:48] first fraction closer to pi has a
[19:50] denominator of more than 16,52,163
[19:54] over 16,64.
[19:58] Records, runs, [music] continued
[19:59] fractions, all of it is the median walk
[20:01] seen from far away.
[20:08] How long is the fairy sequence of order
[20:10] n? Each denominator q contributes the
[20:13] numerators from 1 to q that share no
[20:15] factor with q. That count has a name
[20:18] oiler's toient five of q. So the length
[20:21] is 1 for the 0 + 5 of 1 + 5 of 2 all the
[20:25] way up to five of n. For n= 5, that's 1
[20:28] + 1 1 2 2 and 4 11 matching our list.
[20:33] For n= 100, it's 3,045.
[20:37] There's a cleaner way to see this. Back
[20:39] in the grid, the fairy fractions of
[20:41] order n are the visible points in a
[20:43] triangle on or below the diagonal and no
[20:46] further right than n. That triangle has
[20:48] an area of n^2 over two. So the real
[20:52] question is what share of grid points is
[20:54] visible? A point is hidden exactly when
[20:57] its two coordinates share a factor. So
[20:59] pick two whole numbers at random from
[21:01] one up to some large number. [music]
[21:03] What's the chance that they share no
[21:05] common factor at all? Take a prime say
[21:08] three. Both numbers are multiples of
[21:11] three with probability 1 9th. So they
[21:14] avoid sharing the factor three with
[21:16] probability 1 minus a 9th. The same goes
[21:19] for every prime and divisibility by
[21:21] different primes behaves independently.
[21:23] [music] Made rigorous, the chance of
[21:25] sharing no prime at all is the product
[21:27] over all primes of 1 - 1 over the prime
[21:30] squared. Oiler knew how to evaluate this
[21:33] product. Flip each factor over and it
[21:36] becomes a geometric series. 1 + a/4 + a
[21:39] 16th and so on for the prime two.
[21:42] Multiply all of these series together.
[21:45] By unique factorization, every square
[21:47] number appears exactly once and you get
[21:49] 1 + a/4 plus a 9th plus a 16th and so
[21:52] on. The sum of 1 / k^ 2. In the 1730s,
[21:56] Oiler showed that this sum is p<unk> ^2
[21:58] / 6. So the chance is 6 over pi squared
[22:02] about 61%.
[22:04] Pi from a question about common factors
[22:07] in a 100 by 100 grid the visible share
[22:10] is already 60.87%.
[22:13] And so the fairy sequence of order n has
[22:15] about 6 over<unk> ^ 2 * n ^2 / 2 which
[22:18] is 3 n^2 over<unk> ^ 2 terms. For n= 100
[22:23] that predicts about 3,040.
[22:25] The true count is 3,045.
[22:28] [music] These fractions are spread
[22:30] almost evenly across the interval.
[22:33] Almost.
[22:34] Exactly how evenly turns out to be one
[22:36] of the deepest questions in mathematics.
[22:43] Take the fairy sequence of order n, drop
[22:45] the zero, and number the rest f_sub_1,
[22:48] f_sub_2, and so on up to fm, which is
[22:50] one. If they were perfectly evenly
[22:53] spaced, the kth1 would sit at exactly k
[22:56] over m. [music]
[22:57] They don't quite. So, let's measure how
[23:00] far off they are. For each k, take the
[23:03] distance between fk and k / m and add up
[23:05] all those distances. [music] Here are
[23:08] some computed values. For n= 100, there
[23:11] are 3,044 fractions and the total is
[23:14] about 2.04.
[23:16] For n= 200, about 3.5.
[23:20] For n= 800, with almost 200,000
[23:23] fractions, the total is only about 4.7.
[23:26] The number of fractions grows like n^
[23:28] squ. But in these computations, the
[23:30] total grows far more slowly, roughly
[23:32] like the square root of n. That's an
[23:34] observation from data, not a theorem. In
[23:38] 1924, in a pair of papers, Jerome Fell
[23:41] and Edmund Lando proved something
[23:42] astonishing. The statement that this
[23:45] total stays below a constant time n to
[23:47] the power 1/2 plus epsilon for every
[23:49] positive epsilon is equivalent to the
[23:51] reman hypothesis. [music] The reman
[23:54] hypothesis is a statement about the
[23:55] zeros of the zeta function. The same
[23:57] function whose value at 2 gave us p<unk>
[23:59] ^2 over 6. [music] It controls how
[24:02] regularly the prime numbers are spread
[24:04] out. It has been open since 1859 and
[24:07] it's one of the clay institutees
[24:09] millennium price problems with a million
[24:11] dollar reward. [music] So showing that
[24:13] the fairy fractions are this evenly
[24:15] spread is exactly as hard as proving the
[24:17] reman hypothesis.
[24:19] Nobody has done it. Why would primes
[24:21] care about fractions? Because counting
[24:24] fractions in lowest terms means removing
[24:26] the multiples of each prime and the
[24:28] bookkeeping for that is the moius
[24:30] function. The reman hypothesis is
[24:32] equivalent to the running total of the
[24:34] mobius function staying small. And
[24:36] Franel's work ties the spacing of the
[24:38] ferry fractions to that same running
[24:39] total from a headline about 72.7%
[24:43] to the deepest open problem and number
[24:45] theory all by way of one humble
[24:47] operation adding the [music] tops and
[24:48] adding the bottoms.
[24:54] Let's retrace the path. A rounded
[24:57] percentage is a window. The simplest
[25:00] fraction in a window is found by walking
[25:02] with medians from 0 over 1 and 1 / 1.
[25:05] And the walk is correct because fairy
[25:07] neighbors satisfy B * C minus A * D= 1,
[25:10] which we saw as an area in a grid of
[25:12] points. [music] The same walk draws the
[25:14] ford circles, builds a tree that
[25:16] contains every fraction, finds the best
[25:18] approximations of pi, and in how evenly
[25:20] it spreads the fractions, hides the
[25:22] reman hypothesis. Here's one last
[25:24] example. A poll says 33.3%.
[25:29] That could be just three people, one out
[25:31] of three. Now change one digit. A poll
[25:35] says 33.4%.
[25:38] How many people now? at least 287.
[25:42] 1/3 sits just below the window. So, the
[25:44] walk is stuck taking 95 steps in a row
[25:47] before it reaches 96 over 287.
[25:50] One digit and the smallest possible poll
[25:53] grows nearly a 100fold. Next time you
[25:55] see a percentage in the news, you'll
[25:57] know the question to ask. How many
[25:59] people could that really be? Thanks for
[26:02] watching.
