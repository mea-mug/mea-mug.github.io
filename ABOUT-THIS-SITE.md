# About this site

The new MEA website, built into this kit and ready to publish. For the publishing
setup (GitHub account, token, `PUBLISH.bat`), read **START-HERE.md** — that guide is
unchanged. This file only covers the website itself.

> Do not put your notes in `README.md`. It is rewritten from scratch on every publish.

---

## The pages

Six pages, in `html_files`:

| File | Live address | What it is |
|---|---|---|
| `index.html` | `/` | Home — pitch, what we do, vision, solutions, equipment preview |
| `about.html` | `/about` | Company story, mission / value / standards, the three capabilities |
| `services.html` | `/services` | The five service lines, then study → supervise → execute → advise |
| `equipment.html` | `/equipment` | 32 machines in 6 filterable families, click any photo to enlarge |
| `projects.html` | `/projects` | Photo gallery: workshop, machines built, on site, studies |
| `contact.html` | `/contact` | Direct ways to reach you. No form, no map |

Shared files: `css/site.css` (all styling) and `js/site.js` (all behaviour). Change a
colour or a heading style once in `site.css` and every page follows.

---

## What it does

- **Dark and light mode.** Dark by default. A visitor who has never touched the switch
  follows their own computer's setting; once they click the ☀/☾ button their choice is
  remembered. Both modes are fully styled — check both after any change.
- **English and Arabic.** The ع / EN button swaps every piece of text and flips the whole
  page to right-to-left, with a proper Arabic typeface (Cairo). The choice is remembered.
- **The year updates itself.** The footer reads the real current year, so it can never go
  stale the way `© 2015` did.
- **Equipment filtering.** Six category buttons. Links like `/equipment#food` arrive
  already filtered.
- **Photo lightbox.** Click any equipment or gallery photo. Arrow keys move, Escape closes.
- Sticky header, scroll-in animations, back-to-top button, mobile menu, print stylesheet,
  and reduced-motion support for visitors who ask for less animation.

---

## Editing the text

Every translatable element holds both languages as attributes:

```html
<h3 data-en="Cranes" data-ar="رافعات">Cranes</h3>
```

Change **all three** — `data-en`, `data-ar`, and the visible text between the tags. The
visible text is what shows before the script runs and what search engines read, so it
must match `data-en`.

---

## Changing the contact details

They appear in the footer of all six pages plus the contact page, so use your editor's
"replace in all files":

| Find | Currently |
|---|---|
| e-mail | `info@mea-mug.com` |
| phone link | `tel:+491774648243` |
| phone shown | `+49 177 464 8243` |
| Facebook | `facebook.com/ingenieurwesen.industrie.7` |
| Skype | `mea_said` |

**There is no address and no map anywhere on the site.** The only location statement is
"Based in Germany", which appears on the contact page and in the footer of every page.

---

## No contact form — on purpose

You did not want a form that opens the visitor's e-mail app, so there is none. The contact
page offers the e-mail address and the phone number as two large buttons, plus Skype and
Facebook underneath. On a phone, tapping them starts a mail draft or dials directly.

That also means there is nothing on the site that can silently break: no form endpoint, no
third-party service, no spam to filter.

If you ever do want a real form that lands in your inbox, the usual free option is
<https://web3forms.com>. It needs a `<form>` block on the contact page and one hidden key
field — ask and it can be added back.

---

## One thing to know about the addresses

Every link and image uses an address starting from the site root, like `/css/site.css` and
`/images/equipment/14-cranes.jpg`. That is correct for:

- `https://YOUR-NAME.github.io` (the kit's normal setup), and
- a custom domain such as `https://mea-mug.com`.

It would **not** work if the site were published into a sub-folder, like
`username.github.io/mea-mug/`. If you ever do that, every `/...` address needs the folder
name in front of it. Sticking to the setup in START-HERE.md avoids this entirely.

---

## The images

In `html_files/images`, grouped by section, and every one came from your old site.

- **The white borders are gone.** 29 of the photos had white margins you had added years
  ago; those have been trimmed off automatically, and the pictures now fill their frames.
- **Two sizes of everything.** The full-size file (up to 1600 px) and a `thumbs/` copy
  (up to 700 px). Grids and galleries load the thumbnail; the lightbox loads the full one.
  That is why the site stays quick despite having 70-odd photos.
- **File names describe the picture**, e.g. `equipment/26-biscuit-chips-...-wafer-biscuit.jpg`.
- Total weight is about 6 MB, down from 8.7 MB, at better quality on screen.

A few old files are deliberately **not used**: the grey divider strip, the clip-art
"e-mail / Skype / mobile" icons (replaced with clean symbols), the old Wix page background,
and one small stock photo that came from a Wix account rather than your camera. They are
still in the folder if you want them.

---

## Changes made to the old wording

You asked me to fix these, so for the record:

- **"Supplyer" → "Supplier"**, **"PROQUREMENT" → "Procurement"**, **"Alumnim" → "Aluminium"**,
  and **"concrete patch plants" → "batch plants"**.
- **"Gulf Experts" is gone.** The old About text switched to that name mid-paragraph, which
  read like leftover template copy. Everything now says **MEA** consistently.
- **"SALWA A. AL-SALEH Est." is gone** from every page, since that establishment is no
  longer valid. MEA is now the only name on the site.
- **Saudi Arabia and Riyadh are gone.** The site says **Based in Germany**. The About page
  now refers to the old factory in the past tense, so the workshop photos still make sense
  without claiming you are still there. The workshop-signboard photo was removed from
  Projects because the sign carries the old establishment's name.
- **One e-mail instead of six**, one phone number instead of two sets.
- **The three "Our Vision / Our Services / Our Solutions" pictures were scans of text.**
  Their content is now real text on the Home and Services pages, so it can be read on a
  phone, found by Google, and translated. (The original vision scan was cut off
  mid-sentence when it was first uploaded, so its last line ends early — worth rewriting
  that paragraph when you get a chance.)

---

## Before you publish

- Decide whether `info@mea-mug.com` exists yet. If not, create it, or every e-mail link
  on the site goes nowhere.
- Re-read the Home and About copy in your own voice — it is faithful to the old site, but
  the old site's English was rough in places and I have only tidied it, not rewritten it.
- Have a native Arabic reader skim the Arabic. I based it on your original Arabic where the
  old site had it, and translated the rest.
- A few photos are low-resolution Facebook-era downloads. They are the weakest thing on the
  site now; re-shooting even five or six machines would lift it a lot.

---

## Previewing on your PC before publishing

From this folder:

```bash
python scripts/build_index.py html_files _site unlisted && python -m http.server 8765 --directory _site
```

Then open <http://localhost:8765>. You must view it through this little server rather than
by double-clicking the HTML files, because of the root-relative addresses explained above.
`_site` is a throwaway build folder and is never published from your PC — GitHub rebuilds
it for you on every publish.
