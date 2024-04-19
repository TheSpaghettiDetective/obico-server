/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
import React from 'react';
import Layout from '@theme/Layout';
import BlogPostItem from '../BlogPostItem';
import BlogPostPaginator from '@theme/BlogPostPaginator';
import BlogSidebar from '../BlogSidebar';
import TOC from '@theme/TOC';
import { ThemeClassNames } from '@docusaurus/theme-common';
import clsx from 'clsx';
import styles from './styles.module.css';
import './styles.css';


function BlogPostPage(props) {
  const {content: BlogPostContents, sidebar} = props;
  const {frontMatter, metadata} = BlogPostContents;
  const {title, description, nextItem, prevItem, tags} = metadata;
  const {hide_table_of_contents: hideTableOfContents} = frontMatter;
  return (
    <Layout
      title={title}
      description={description}
      wrapperClassName={ThemeClassNames.wrapper.blogPages, 'blog-post-with-bg'}
      pageClassName={ThemeClassNames.page.blogPostPage}>
      {BlogPostContents && (
        <div className="container margin-vert--lg">
          <div className="row">
            {!hideTableOfContents && BlogPostContents.toc && (
              <div className="col col--2">
                <TOC toc={BlogPostContents.toc} />
              </div>
            )}
            <main className={clsx(styles.blogPost, 'col col--7')}>
              <BlogPostItem
                frontMatter={frontMatter}
                metadata={metadata}
                isBlogPostPage>
                <BlogPostContents />
              </BlogPostItem>

              {(nextItem || prevItem) && (
                <BlogPostPaginator nextItem={nextItem} prevItem={prevItem} />
              )}
            </main>
            <aside className="col col--3">
              <BlogSidebar sidebar={sidebar} tags={tags} />
            </aside>
          </div>
        </div>
      )}
    </Layout>
  );
}

export default BlogPostPage;
