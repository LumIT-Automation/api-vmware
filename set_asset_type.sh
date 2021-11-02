#!/bin/bash


skelAssetType="assetType"
assetType="vmware"

SkelAssetType="AssetType"
AssetType="VMware"

skelAssetSlice="assetSlice"
assetSlice="vmFolder"

SkelAssetSlice="AssetSlice"
AssetSlice="VMFolder"

# Rename directories first.
find . -type d -name "*${skelAssetType}*" -exec bash -c "
    oldName=\$1
    newName=\`echo \$oldName | sed \"s/${skelAssetType}/${assetType}/g\"\`
    mv -v \"\$oldName\" \"\$newName\"
    " bash {} \; 

find . -type d -name "*${SkelAssetType}*" -exec bash -c "
    oldName=\$1
    newName=\`echo \$oldName | sed \"s/${SkelAssetType}/${AssetType}/g\"\`
    mv \"\$oldName\" \"\$newName\"
    " bash {} \; 

find . -type d -name "*${skelAssetSlice}*" -exec bash -c "
    oldName=\$1
    newName=\`echo \$oldName | sed \"s/${skelAssetSlice}/${assetSlice}/g\"\`
    mv \"\$oldName\" \"\$newName\"
    " bash {} \; 

find . -type d -name "*${SkelAssetSlice}*" -exec bash -c "
    oldName=\$1
    newName=\`echo \$oldName | sed \"s/${SkelAssetSlice}/${AssetSlice}/g\"\`
    mv \"\$oldName\" \"\$newName\"
    " bash {} \; 


# Rename files.
find . -type f -name "*${skelAssetType}*" -exec bash -c "
    oldName=\$1
    newName=\`echo \$oldName | sed \"s/${skelAssetType}/${assetType}/g\"\`
    mv \"\$oldName\" \"\$newName\"
    " bash {} \; 

find . -type f -name "*${SkelAssetType}*" -exec bash -c "
    oldName=\$1
    newName=\`echo \$oldName | sed \"s/${SkelAssetType}/${AssetType}/g\"\`
    mv \"\$oldName\" \"\$newName\"
    " bash {} \; 

find . -type f -name "*${skelAssetSlice}*" -exec bash -c "
    oldName=\$1
    newName=\`echo \$oldName | sed \"s/${skelAssetSlice}/${assetSlice}/g\"\`
    mv \"\$oldName\" \"\$newName\"
    " bash {} \; 

find . -type f -name "*${SkelAssetSlice}*" -exec bash -c "
    oldName=\$1
    newName=\`echo \$oldName | sed \"s/${SkelAssetSlice}/${AssetSlice}/g\"\`
    mv \"\$oldName\" \"\$newName\"
    " bash {} \; 

# Change files (exclude this one only).
find . -type f ! -name `basename $0` -exec sed -i -e "s/${skelAssetType}/${assetType}/g" -e "s/${SkelAssetType}/${AssetType}/g" -e "s/${skelAssetSlice}/${assetSlice}/g" -e "s/${SkelAssetSlice}/${AssetSlice}/g" {} \;




