import os
import numpy as np
import cv2
import math

def DCmakedir(path):
    if os.path.exists(path):
        return
    else:
        os.mkdir(path)

def imageRotate(img,theta):
    rows,cols = img.shape[0:2]
    angle = -theta*math.pi/180
    a = math.sin(angle)
    b = math.cos(angle)
    width = int(cols * math.fabs(b) + rows * math.fabs(a))
    heigth = int(rows * math.fabs(b) + cols * math.fabs(a))
    M = cv2.getRotationMatrix2D((width/2,heigth/2),theta,1)
    rot_move = np.dot(M,np.array([(width-cols)*0.5,(heigth-rows)*0.5,0]))
    M[0,2] += rot_move[0]
    M[1, 2] += rot_move[1]
    imgout_xuanzhuan = cv2.warpAffine(img,M,(width,heigth),2,0,0)
    return imgout_xuanzhuan


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))

def perspective_trans(img):
    y1,x1 = img.shape[0:2]
    pts1 = np.float32([[0,0],[x1,0],[0,y1],[x1,y1]])


    x2_1 = np.random.randint(0, int(x1 / 6))
    y2_1 = np.random.randint(0, int(y1 / 6))

    x2_2 = np.random.randint(0, int(x1 / 6))
    y2_2 = np.random.randint(0, int(y1 / 6))

    x2_3 = np.random.randint(0, int(x1 / 6))
    y2_3 = np.random.randint(0, int(y1 / 6))

    x2_4 = np.random.randint(0, int(x1 / 6))
    y2_4 = np.random.randint(0, int(y1 / 6))

    pts2 = np.float32([[x2_1, y2_1], [x1-x2_2, y2_2],
                       [x2_3, y1-y2_3], [x1-x2_4, y1-y2_4]])
    MM = cv2.getPerspectiveTransform(pts1,pts2)
    #print(MM)
    imgout_p = cv2.warpPerspective(img,MM,(x1,y1))#,cv2.INTER_LINEAR,0,0
    imgout = imgout_p[min(y2_1,y2_2):y1 -min(y2_3,y2_4),min(x2_1,x2_3):x1-min(x2_2,x2_4)]
    imgout = cv2.resize(imgout,(y1,x1))
    return imgout


def online_data_generate(fgpath,bgpath,fgImglist,bgImglist,fgImgNum,bgImgNum):
  returnImg = False
  while(not returnImg):
    randomfgIndex = np.random.randint(0,fgImgNum)
    randombgIndex = np.random.randint(0,bgImgNum)
    fgImg = cv2.imdecode(np.fromfile(os.path.join(fgpath,fgImglist[randomfgIndex]), dtype=np.uint8), -1) 
    #cv2.imread(os.path.join(fgpath,fgImglist[randomfgIndex]),cv2.IMREAD_COLOR)
    bgImg = cv2.imdecode(np.fromfile(os.path.join(bgpath,bgImglist[randombgIndex]), dtype=np.uint8), -1) 
    #cv2.imread(os.path.join(bgpath,bgImglist[randombgIndex]),cv2.IMREAD_COLOR)
    try:
        fgImg.shape
        bgImg.shape
        #print("fgImg.shape",fgImg.shape)
        #print("bgImg.shape",bgImg.shape)
        
    except:
        continue
    try:
      if (bgImg.shape[0]<520 or bgImg.shape[1]<520):
          #print("bgImg:",bgImg.shape)
          if(bgImg.shape[0]< bgImg.shape[1]) :
              #print("fx=800./bgImg.shape[0], fy=800./bgImg.shape[0]",800./bgImg.shape[0], 800./bgImg.shape[0])
              bgImg = cv2.resize(bgImg,(0, 0), fx=800./bgImg.shape[0], fy=800./bgImg.shape[0])
          else:
             # print("fx=800./bgImg.shape[1], fy=800./bgImg.shape[1]",800./bgImg.shape[1], 800./bgImg.shape[1])
              bgImg = cv2.resize(bgImg,(0, 0), fx=800./bgImg.shape[1], fy=800./bgImg.shape[1])
      #print(bgImg.shape)
      bg_cut_r = np.random.randint(0,int(bgImg.shape[1]-512))
      bg_cut_c = np.random.randint(0,int(bgImg.shape[0]-512))
      bgImg = bgImg[bg_cut_c:bg_cut_c+512,bg_cut_r:bg_cut_r+512,:]
      
      M = np.ones(fgImg.shape,dtype="uint8")*5
      fgImg = cv2.add(fgImg,M)
      need_per = np.random.randint(1,5)
      
      if need_per%2==0:
          #print("perspective_trans fgImg.shape",fgImg.shape)
          img = perspective_trans(fgImg)
      else:
          img = fgImg
      need_rotata = np.random.randint(1,5)
      if need_rotata%2==0:
          theta = np.random.randint(1,30)
          img = rotate_bound(img,theta)
      else:
          theta = 1
          img = rotate_bound(img,theta)
      
      
      fgcols,fgrows = img.shape[0:2]
      #print("fgrows,fgcols",fgrows,fgcols)
      bgcols,bgrows= bgImg.shape[0:2]
      
      #print("bgrows,bgcols",bgrows,bgcols)
      
      fgLongSideRatio = 0.7+(1.0-0.7)*np.random.random()
      
      
      if float(fgrows)/bgrows >float(fgcols)/bgcols:
          #print("fgrows/bgrows ,fgcols/bgcols)",float(fgrows)/bgrows ,float(fgcols)/bgcols)
          fg_r = int(bgrows*fgLongSideRatio)
          fg_c = int(float(fg_r)/fgrows *fgcols)
      else:
          #print("fgrows/bgrows ,fgcols/bgcols)",float(fgrows)/bgrows ,float(fgcols)/bgcols)
          fg_c = int(bgcols*fgLongSideRatio)
          fg_r = int(float(fg_c)/fgcols *fgrows)
      #print("fg_r,fg_c",fg_r,fg_c)
      fgimg = cv2.resize(img,(fg_r,fg_c))
      gray = cv2.cvtColor(fgimg,cv2.COLOR_BGR2GRAY)
      _,mask1 = cv2.threshold(gray,1,255,cv2.THRESH_BINARY)
      
      mask1[0:8,:] = 0
      mask1[:,0:8] = 0
      mask1[mask1.shape[0]-9:mask1.shape[0],:] = 0
      mask1[:,mask1.shape[1]-9:mask1.shape[1]] = 0
      
      
      kernel = np.ones((5,5),np.uint8)
      mask = cv2.erode(mask1,kernel,iterations = 3)
      edge = cv2.absdiff(mask,mask1)
      mask_inv = cv2.bitwise_not(mask)
      bord_r = np.random.randint(0,bgrows-fg_r)
      bord_c = np.random.randint(0,bgcols-fg_c)
      bord_r2 = bord_r+fg_r
      bord_c2 = bord_c+fg_c
      
      
      
      
      roi = bgImg[bord_c:bord_c2, bord_r:bord_r2]
      img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
      img2_fg = cv2.bitwise_and(fgimg,fgimg,mask = mask)
      dst = cv2.add(img1_bg,img2_fg)
      edgeOut = np.zeros(bgImg.shape[0:2],dtype="uint8")
      edgeOut[bord_c:bord_c2,bord_r:bord_r2 ]= edge 
      bgImg[bord_c:bord_c2,bord_r:bord_r2 ]= dst
      if bgImg.shape[2]!=3:
        continue
      returnImg = True   
    except:
        continue        
  return bgImg,edgeOut
#    cv2.imwrite(os.path.join(saveImgpath,"img_"+str(index))+".jpg",bgImg)
#    edgeOut = np.zeros(bgImg.shape[0:2],dtype="uint8")
#    edgeOut[bord_c:bord_c2,bord_r:bord_r2 ]= edge
#    cv2.imwrite(os.path.join(saveEdgepath,"img_"+str(index)+".bmp"),edgeOut)
#    print("image",index,"is saved to",saveImgpath+"/img_"+str(index)+".bmp")
